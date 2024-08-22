from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import UserRegistrationSerializer, TaskSerializer
from .models import Task, User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings

# HTML Views


def menu_list(request):
    context={}
    context['baseurl']= settings.BASE_URL
    return render(request, 'menu_list.html',context)


def user_register_view(request):
    context={}
    context['baseurl']= settings.BASE_URL
    return render(request, 'user_register.html',context)

def user_login_view(request):
    context={}
    context['baseurl']= settings.BASE_URL
    return render(request, 'user_login.html',context)

def task_view_list(request):
    context={}
    # Fetch the tasks created by the user
    tasks = Task.objects.filter(created_by=request.user.id).values('id', 'title','status')

    # Prepare the context
    task_list = []

    for task in tasks:
        # Fetch usernames for each task's members
        task_instance = Task.objects.get(id=task['id'])
        member_ids = task_instance.members.values_list('id', flat=True)  # This should return a list of IDs

        if member_ids is None:
            member_ids = []  # Ensure member_ids is an iterable, even if empty
        
        member_usernames = User.objects.filter(id__in=member_ids).values_list('username', flat=True)
        
        # Add usernames to the task data
        task_data = {
            'id': task['id'],
            'title': task['title'],
            'status': task['status'],
            'members': list(member_usernames)  # Convert queryset to list
        }
        task_list.append(task_data)

    context['taskId']= task_list # Move context assignment outside of the loop
    try:
        token=Token.objects.get(user_id=request.user.id)
        context['token']=token.key
    except Token.DoesNotExist:
        token = None
    context['baseurl']= settings.BASE_URL
    return render(request, 'taskList.html', context)


def create_task_view(request):
    context = {}
    try:
        token=Token.objects.get(user_id=request.user.id)
        context['token']=token.key
    except Token.DoesNotExist:
        token = None

    all_users = User.objects.all()
    context['all_users'] = all_users
    context['login_id'] = request.user.id
    context['baseurl']= settings.BASE_URL
    return render(request, 'create_task.html', context)

def manage_members_view(request):
    context = {}
    try:
        token=Token.objects.get(user_id=request.user.id)
        context['token']=token.key
    except Token.DoesNotExist:
        token = None
    taskId=Task.objects.filter(created_by=request.user.id).values('id', 'title')
    context['taskId']=taskId
    return render(request, 'manage_members.html', context)

def logout_view(request):
    try:
        messages.success(request, 'You have successfully logged out!', extra_tags='success')
        logout(request)
    except Exception as e:
        print(e)
    return redirect('/login/')

# API Views

@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)  # Set up the session if you are using session-based authentication
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)  # Associate the task with the authenticated user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_list(request):
    tasks = Task.objects.filter(created_by=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskSerializer(task)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_task_member(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user_ids = request.data.get('user_ids', [])
    users = User.objects.filter(id__in=user_ids)
    task.members.add(*users)
    return Response({'status': 'Members added'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_task_member(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user_ids = request.data.get('user_ids', [])
    users = User.objects.filter(id__in=user_ids)
    task.members.remove(*users)
    return Response({'status': 'Members removed'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_task_members(request, pk):
    task = get_object_or_404(Task, pk=pk)
    members = task.members.all()
    member_data = [{'id': member.id, 'username': member.username} for member in members]
    return Response(member_data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        task_status = serializer.validated_data.get('status')
        if task_status not in ['todo', 'inprogress', 'done']:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"message": "Task status updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
