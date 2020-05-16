from rest_framework import serializers

from pznsi.models import Environment, Project, Comment, User, Attachment, Vote


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'avatar']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['user', 'comment_title', 'comment_content', 'comment_reaction', 'comment_date']


class AttachmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Attachment
        fields = ['user', 'content', 'attachment_creation_date']


class VoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    # TODO add averages methodfield
    class Meta:
        model = Vote
        fields = ['user', 'vote_date', 'vote_content']


class ProjectDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(source='comment_set', many=True, required=False)
    environment_name = serializers.SlugRelatedField(source='environment', slug_field='environment_name', read_only=True)
    owner = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(source='attachment_set', many=True, required=False, read_only=True)
    votes = VoteSerializer(source='vote_set', many=True, required=False, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_status', 'project_category', 'project_content', 'comments',
                  'cover_image', 'environment', 'environment_name', 'owner', 'attachments', 'votes']

    def create(self, validated_data):
        validated_data.pop('comment_set', None)
        project = Project.objects.create(**validated_data)
        return project


class ProjectBasicsSerializers(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'owner', 'project_content', 'cover_image']


class EnvironmentSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Environment
        fields = ['id', 'environment_name', 'projects', 'owner', 'cover_image']

    def create(self, validated_data):
        validated_data.pop('project_set', None)
        environment = Environment.objects.create(**validated_data)
        return environment

    def get_projects(self, obj):
        projects = obj.get_projects(self.context['request'].user)
        return ProjectBasicsSerializers(projects, many=True).data
