import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import QueryDict
from asgiref.sync import async_to_sync
import requests

from django.contrib.gis.geoip2 import GeoIP2

g = GeoIP2()

from .models import *

from channels.db import database_sync_to_async
from django.core import serializers

from datetime import date


class LiveUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        params = QueryDict(self.scope['query_string'].decode())
        app_name = params.get('app_name')
        api_key = params.get('api_key')
        admin = params.get('admin')
        
        self.scope['session']['layer'] = app_name
        self.scope['session']['admin'] = True if admin == 'true' else False


        await self.channel_layer.group_add(
            app_name,
            self.channel_name
        )

        await self.accept()

        print("connection established")


    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        header = text_data_json['header']
        if header == "live-user-data":
            os = text_data_json['os']
            browser = text_data_json['Browser']
            mobile = text_data_json['Mobile']
            self.scope['session']['mobile'] = mobile

            print("working")
            ip = requests.get('https://api.ipify.org/').text
            self.scope['session']['ip'] = ip

            city = g.city(ip)['city']
            country = g.country(ip)
            coordinates = g.coords(ip)

            await self.save_live_counts(os,browser,mobile,ip,city,country,coordinates)
            print("working")

            statics, serialized_locations = await database_sync_to_async(self.get_live_counts)()

            await self.channel_layer.group_send(self.scope['session']['layer'],{
                'type': 'live_statics',
                'header': 'statistics',
                'user_count': statics.user,
                'desktop_count': statics.desktop,
                'mobile_count': statics.mobile,
                'locations': serialized_locations,
            })
        elif header == "get-stats":
            print("get status")

    


    async def disconnect(self, code):
        print("connectin closed")

        await self.channel_layer.group_discard(
            self.scope['session']['layer'],
            self.channel_name
        )

        if self.scope['session']['admin'] == False:
            await self.save_removed_live_counts()

        statics, serialized_locations = await database_sync_to_async(self.get_live_counts)()

        await self.channel_layer.group_send(self.scope['session']['layer'],{
            'type': 'live_statics',
            'header': 'statistics',
            'user_count': statics.user,
            'desktop_count': statics.desktop,
            'mobile_count': statics.mobile,
            'locations': serialized_locations,
        })

    async def live_statics(self,event):
        header = event['header']
        user_count = event['user_count']
        desktop_count = event['desktop_count']
        mobile_count = event['mobile_count']
        locations = event['locations'],


        await self.send(text_data=json.dumps({
            'header': header,
            'user_count': user_count,
            'desktop_count': desktop_count,
            'mobile_count': mobile_count,
            'locations': locations,
        }))

    def get_live_counts(self):
        app = App.objects.get(name=self.scope['session']['layer'])
        live_counts = Live_Counts.objects.get(app=app)
        locations = live_counts.locations.all()
        serialized_locations = serializers.serialize('json',locations)
        return live_counts,serialized_locations

    
    @database_sync_to_async
    def add_live_counts(self,os,browser,mobile,ip,city,country,coordinates):
        app = App.objects.get(name=self.scope['session']['layer'])
        live_counts,_ = Live_Counts.objects.get_or_create(app=app)
        live_counts.user += 1

        if mobile == "true":
            live_counts.mobile += 1 
        else:
            live_counts.desktop += 1

        location = Locations.objects.create(
            city = city,
            country = country["country_name"],
            longtitute = coordinates[0],
            lattitute = coordinates[1]
        )
        self.scope['session']['location_object_id'] = location.pk
        live_counts.locations.add(location)

        ip_object = IP.objects.create(
            address = ip
        )
        self.scope['session']['ip_object_id'] = ip_object.pk
        live_counts.ip_addresses.add(ip_object)

        live_counts.save()

        dailylocation = DailyLocations.objects.create(
            city = city,
            country = country["country_name"],
            longtitute = coordinates[0],
            lattitute = coordinates[1]
        )

        counts,_ = Counts.objects.get_or_create(app=app,date=date.today())
        counts.user += 1
        counts.desktop += 1
        counts.mobile += 1
        counts.locations.add(dailylocation)
        counts.save()

        return live_counts

    async def save_live_counts(self,os,browser,mobile,ip,city,country,coordinates):
        await self.add_live_counts(os,browser,mobile,ip,city,country,coordinates)

    @database_sync_to_async
    def remove_live_counts(self):
        if self.scope['session']['ip']:

            ip = self.scope['session']['ip']

            app = App.objects.get(name=self.scope['session']['layer'])
            live_counts = Live_Counts.objects.get(app=app)
            live_counts.user -= 1
            if self.scope['session']['mobile'] == "true":
                live_counts.mobile -= 1 
            else:
                live_counts.desktop -= 1

            location = Locations.objects.get(pk=self.scope['session']['location_object_id'])
            live_counts.locations.remove(location)

            ip_object = IP.objects.get(pk=self.scope['session']['ip_object_id'])
            live_counts.ip_addresses.remove(ip_object)

            live_counts.save()

            location.delete()
            ip_object.delete()
            return live_counts
        return False

    async def save_removed_live_counts(self):
        await self.remove_live_counts()