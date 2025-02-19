"""
Serializers for the edx-exams API
"""
from rest_framework import serializers
from rest_framework.fields import DateTimeField

from edx_exams.apps.api.constants import ASSESSMENT_CONTROL_CODES
from edx_exams.apps.core.api import get_exam_attempt_time_remaining, get_exam_url_path
from edx_exams.apps.core.exam_types import EXAM_TYPES
from edx_exams.apps.core.models import AssessmentControlResult, Exam, ExamAttempt, ProctoringProvider, User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User Model.
    """
    id = serializers.IntegerField(required=False)  # pylint: disable=invalid-name
    lms_user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        """
        Meta Class
        """
        model = User

        fields = (
            'id', 'username', 'email', 'lms_user_id'
        )


class ProctoringProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProctoringProvider Model
    """

    class Meta:
        model = ProctoringProvider
        fields = ['name', 'verbose_name', 'lti_configuration_id']


class ExamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Exam Model
    """

    exam_name = serializers.CharField(required=True)
    course_id = serializers.CharField(required=False)
    content_id = serializers.CharField(required=True)
    time_limit_mins = serializers.IntegerField(required=True)
    due_date = serializers.DateTimeField(required=True, allow_null=True)
    exam_type = serializers.CharField(required=True)
    hide_after_due = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)

    class Meta:
        """
        Meta Class
        """

        model = Exam

        fields = (
            'id', 'exam_name', 'course_id', 'content_id', 'time_limit_mins', 'due_date', 'exam_type',
            'hide_after_due', 'is_active'
        )

    def validate_exam_type(self, value):
        """
        Validate that exam_type is one of the predefined choices
        """
        valid_exam_types = [exam_type.name for exam_type in EXAM_TYPES]
        if value not in valid_exam_types:
            raise serializers.ValidationError('Must be a valid exam type.')
        return value


class ExamAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExamAttempt Model
    """
    exam = ExamSerializer()
    user = UserSerializer()

    start_time = DateTimeField(format=None)
    end_time = DateTimeField(format=None)

    class Meta:
        """
        Meta Class
        """
        model = ExamAttempt

        fields = (
            'id', 'created', 'modified', 'user', 'start_time', 'end_time',
            'status', 'exam', 'allowed_time_limit_mins', 'attempt_number'
        )


class AssessmentControlReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for AssessmentControlResult as a review. Currently a single
    ACS response is equivalent to a review but this may change if we introduce
    multiple ACS responses per attempt.
    """

    submission_time = DateTimeField(source='incident_time', format=None)
    severity = serializers.DecimalField(max_digits=3, decimal_places=2)
    submission_reason = serializers.SerializerMethodField()

    def get_submission_reason(self, obj):
        """
        Get display message from the reason code.
        """
        return ASSESSMENT_CONTROL_CODES.get(obj.reason_code, obj.reason_code)

    class Meta:
        """
        Meta Class
        """
        model = AssessmentControlResult

        fields = (
            'submission_time', 'severity', 'submission_reason'
        )


class StudentAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExamAttempt model containing additional fields needed for the frontend UI
    """

    # directly from the ExamAttempt Model
    attempt_id = serializers.IntegerField(source='id')
    attempt_status = serializers.CharField(source='status')

    # custom fields based on the ExamAttemptModel
    course_id = serializers.SerializerMethodField()
    exam_type = serializers.SerializerMethodField()
    exam_display_name = serializers.SerializerMethodField()
    exam_url_path = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()

    def get_course_id(self, obj):
        return obj.exam.course_id

    def get_exam_type(self, obj):
        return obj.exam.exam_type

    def get_exam_display_name(self, obj):
        return obj.exam.exam_name

    def get_exam_url_path(self, obj):
        return get_exam_url_path(obj.exam.course_id, obj.exam.content_id)

    def get_time_remaining_seconds(self, obj):
        return get_exam_attempt_time_remaining(obj)

    class Meta:
        """
        Meta Class
        """
        model = ExamAttempt

        fields = (
            'attempt_id', 'attempt_status', 'course_id', 'exam_type',
            'exam_display_name', 'exam_url_path', 'time_remaining_seconds'
        )


class InstructorViewAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExamAttempt model containing fields needed for the instructor view
    """

    # directly from the ExamAttempt Model
    attempt_id = serializers.IntegerField(source='id')
    attempt_status = serializers.CharField(source='status')
    start_time = DateTimeField(format=None)
    end_time = DateTimeField(format=None)
    allowed_time_limit_mins = serializers.IntegerField()

    # fields based on the ExamModel
    exam_type = serializers.CharField(source='exam.exam_type')
    exam_display_name = serializers.CharField(source='exam.exam_name')

    # fields based on the UserModel
    username = serializers.CharField(source='user.username')

    # review information
    proctored_review = serializers.SerializerMethodField()

    def get_proctored_review(self, obj):
        """
        Get the proctored review information for the attempt
        """
        review = obj.assessmentcontrolresult_set.first()
        return AssessmentControlReviewSerializer(review).data if review else None

    class Meta:
        """
        Meta Class
        """
        model = ExamAttempt

        fields = (
            'attempt_id', 'attempt_status', 'start_time', 'end_time',
            'allowed_time_limit_mins', 'exam_type', 'exam_display_name', 'username',
            'proctored_review',
        )
