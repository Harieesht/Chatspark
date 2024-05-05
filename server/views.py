from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError,AuthenticationFailed
from rest_framework.response import Response
from django.db.models import Count
from .models import *
from .serializer import *
from .schema import server_list_docs

class ServerListViewSet(viewsets.ViewSet):
    
    queryset=Server.objects.all()
    @server_list_docs
    def list(self,request):
        """
        Handles GET requests to retrieve a list of servers.

        Parameters:
        - request: HttpRequest object containing the request data.

        Query Parameters:
        - category: Optional. Filter servers by category name.
        - qty: Optional. Limit the number of servers returned.
        - by_user: Optional. Filter servers by the requesting user (requires authentication).
        - by_serverid: Optional. Filter servers by server ID.
        - with_num_members: Optional. Include the count of members in each server.

        Raises:
        - AuthenticationFailed: If 'by_user' or 'by_serverid' is provided and the request user is not authenticated.
        - ValidationError: If an invalid server ID is provided.

        Returns:
        - Response object containing serialized server data.

        Note:
        - If 'by_user' is provided, it filters servers by the requesting user's ID.
        - If 'with_num_members' is provided, it includes the count of members in each server.
        - If 'qty' is provided, it limits the number of servers returned.
        - If 'by_serverid' is provided, it filters servers by the provided ID. Raises ValidationError if the ID is invalid.
        """
        category=request.query_params.get("category")
        qty=request.query_params.get("qty")
        by_user=request.query_params.get("by_user")=="true"
        by_serverid=request.query_params.get("by_serverid")
        with_num_members=request.query_params.get("with_num_members")=="true"
        
        
        
        
        if by_user or by_serverid and not request.user.is_authenticated:
            raise AuthenticationFailed()
        
        if category:
            self.queryset=self.queryset.filter(category__name=category)
        
        if by_user:
            user_id=request.user.id
            self.queryset=self.queryset.filter(member=user_id)
        
        if with_num_members:
            self.queryset=self.queryset.annotate(num_members=Count("member"))
        
        if qty:
            self.queryset=self.queryset[:int(qty)]
            
        if by_serverid:
            try:
                self.queryset=self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except ValueError:
                raise ValidationError(detail="Server value error")        
        
        serializer =ServerSerializer(self.queryset,many=True,context={"num_members":with_num_members})
        return Response(serializer.data)
            