from django.db.models import Avg
from rest_framework import serializers

from pznsi.models import Environment, Project, Comment, User, Attachment, Vote


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date = serializers.DateTimeField(source='comment_date')

    class Meta:
        model = Comment
        fields = ['user', 'comment_title', 'comment_content', 'comment_reaction', 'date']


class AttachmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    date = serializers.DateTimeField(source='attachment_creation_date')
    content = serializers.URLField(read_only=True, source='content.url')

    class Meta:
        model = Attachment
        fields = ['user', 'content', 'date']


class VoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ['user', 'vote_date', 'vote_content']


class ProjectDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(source='comment_set', many=True, required=False)
    environment_name = serializers.SlugRelatedField(source='environment', slug_field='environment_name', read_only=True)
    owner = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(source='attachment_set', many=True, required=False, read_only=True)
    votes = VoteSerializer(source='vote_set', many=True, required=False, read_only=True)
    cover_image = serializers.SerializerMethodField()
    can_vote = serializers.SerializerMethodField()
    vote_average = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_status', 'project_category', 'project_content', 'can_vote',
                  'vote_average', 'cover_image', 'environment', 'environment_name', 'owner', 'comments', 'attachments',
                  'votes']

    def create(self, validated_data):
        validated_data.pop('comment_set', None)
        project = Project.objects.create(**validated_data)
        return project

    def get_cover_image(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None

    def get_can_vote(self, obj):
        user = self.context['request'].user
        if user.has_perm('vote', obj):
            return True
        else:
            return False

    def get_vote_average(self, obj):
        votes = obj.vote_set
        return votes.aggregate(Avg('vote_content'))["vote_content__avg"]


class ProjectBasicsSerializers(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'owner', 'project_content', 'cover_image']

    def get_cover_image(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None


class EnvironmentSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)
    cover_image = serializers.SerializerMethodField()
    current_user = serializers.SerializerMethodField()

    class Meta:
        model = Environment
        fields = ['id', 'environment_name', 'projects', 'cover_image', 'owner', 'current_user']

    def create(self, validated_data):
        validated_data.pop('project_set', None)
        environment = Environment.objects.create(**validated_data)
        return environment

    def get_projects(self, obj):
        projects = obj.get_projects(self.context['request'].user)
        return ProjectBasicsSerializers(projects, many=True).data

    def get_cover_image(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None

    def get_current_user(self, obj):
        user = self.context['request'].user
        return UserSerializer(user).data
