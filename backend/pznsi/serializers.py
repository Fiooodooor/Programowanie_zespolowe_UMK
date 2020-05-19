from rest_framework import serializers

from pznsi.models import Environment, Project, Comment, User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name']


class ProjectBasicsSerializers(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'owner', 'project_content', 'cover_image']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'comment_title', 'comment_content', 'comment_reaction', 'comment_date']


class ProjectDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(source='comment_set', many=True, required=False)
    environment_name = serializers.StringRelatedField(source='environment')

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_status', 'project_category', 'project_content', 'comments', 'owner',
                  'cover_image', 'environment', 'environment_name']

    def create(self, validated_data):
        validated_data.pop('comment_set', None)
        project = Project.objects.create(**validated_data)
        return project


class EnvironmentSerializer(serializers.ModelSerializer):
    projects = ProjectBasicsSerializers(source='project_set', many=True, required=False)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Environment
        fields = ['id', 'environment_name', 'projects', 'owner', 'cover_image']

    def create(self, validated_data):
        validated_data.pop('project_set', None)
        environment = Environment.objects.create(**validated_data)
        return environment


