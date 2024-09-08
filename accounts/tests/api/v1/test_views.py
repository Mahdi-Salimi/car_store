import pytest
from unittest.mock import patch, ANY
from unittest import mock

from django.urls import reverse
from django.test import override_settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import OTP, User
from accounts.models import BuyerUserProfile
from django.contrib.auth.tokens import default_token_generator

from accounts.tests.fixtures.fixtures_data import *


@pytest.mark.django_db
def test_register_view_success(api_client):
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'password': '1234QWas@#',
        'password2': '1234QWas@#',
        'user_type': 'b'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access_token' in response.data
    assert 'refresh_token' in response.data


@pytest.mark.django_db
def test_register_view_missing_field(api_client):
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'user_type': 'b'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_view_duplicate_email(api_client, buyer_user):
    url = reverse('register')
    data = {
        'email': buyer_user.email,
        'password': 'newpassword',
        'user_type': 'b'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
def test_login_view_success(api_client, buyer_user):
    url = reverse('login')
    data = {
        'email': buyer_user.email,
        'password': '1234QWas@#'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
def test_login_view_invalid_credentials(api_client, buyer_user):
    url = reverse('login')
    data = {
        'email': buyer_user.email,
        'password': 'wrongpassword'
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'token' not in response.data


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}})
def test_login_view_missing_field(api_client):
    url = reverse('login')
    data = {
        'email': 'buyer@example.com',
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_custom_user_detail_view_success(auth_client, buyer_user):
    url = reverse('user-detail')
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == buyer_user.email


@pytest.mark.django_db
def test_custom_user_detail_view_unauthenticated(api_client):
    url = reverse('user-detail')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_custom_user_detail_view_update_success(auth_client, buyer_user):
    url = reverse('user-detail')
    data = {
        'phone_number': '09123453434'
    }
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['phone_number'] == '09123453434'


@pytest.mark.django_db
def test_custom_user_detail_view_update_invalid(auth_client, buyer_user):
    url = reverse('user-detail')
    data = {
        'email': ''
    }
    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_token_refresh_view_success(api_client, buyer_user):
    url = reverse('token_refresh')
    refresh = RefreshToken.for_user(buyer_user)
    data = {'refresh': str(refresh)}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data


@pytest.mark.django_db
def test_token_refresh_view_invalid_token(api_client, refresh_token):
    url = reverse('token_refresh')
    data = {'refresh': 'invalidtoken'}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_send_otp_success(api_client, buyer_user, mocker):
    url = reverse('send-otp-login')
    mock_send_email = mocker.patch('accounts.api.v1.views.send_otp_email.delay')

    data = {'email': buyer_user.email}
    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        response = api_client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == "OTP sent successfully."
    mock_send_email.assert_called_once_with(buyer_user.email, ANY)


@pytest.mark.django_db
def test_send_otp_nonexistent_email(api_client):
    url = reverse('send-otp-login')
    data = {'email': 'nonexistent@example.com'}
    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_send_otp_missing_email(api_client):
    url = reverse('send-otp-login')
    data = {}
    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_send_otp_invalid_email_format(api_client):
    url = reverse('send-otp-login')
    data = {'email': 'invalid-email'}
    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_verify_otp_success(api_client, buyer_user, mocker):
    url = reverse('verify-otp-login')
    otp = '123456'
    mocker.patch('accounts.api.v1.views.generate_otp', return_value=otp)
    mocker.patch('accounts.api.v1.views.send_otp_email.delay')

    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        api_client.post(reverse('send-otp-login'), {'email': buyer_user.email})

    otp_record = OTP.objects.filter(user=buyer_user).latest('created_at')
    otp_record.set_otp(otp)
    otp_record.save()

    data = {'email': buyer_user.email, 'otp': otp}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in response.data
    assert 'refresh_token' in response.data


@pytest.mark.django_db
def test_verify_otp_invalid_otp(api_client, buyer_user, mocker):
    url = reverse('verify-otp-login')
    otp = '123456'
    mocker.patch('accounts.api.v1.views.generate_otp', return_value=otp)
    mocker.patch('accounts.api.v1.views.send_otp_email.delay')

    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        api_client.post(reverse('send-otp-login'), {'email': buyer_user.email})

    data = {'email': buyer_user.email, 'otp': '654321'}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data


@pytest.mark.django_db
def test_verify_otp_expired_otp(api_client, buyer_user, mocker):
    url = reverse('verify-otp-login')
    otp = '123456'
    mocker.patch('accounts.api.v1.views.generate_otp', return_value=otp)
    mocker.patch('accounts.api.v1.views.send_otp_email.delay')

    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        api_client.post(reverse('send-otp-login'), {'email': buyer_user.email})

    otp_record = OTP.objects.filter(user=buyer_user).latest('created_at')
    otp_record.created_at = timezone.now() - timezone.timedelta(minutes=3)
    otp_record.save()

    data = {'email': buyer_user.email, 'otp': otp}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data


@pytest.mark.django_db
def test_verify_otp_already_used(api_client, buyer_user, mocker):
    url = reverse('verify-otp-login')
    otp = '123456'
    mocker.patch('accounts.api.v1.views.generate_otp', return_value=otp)
    mocker.patch('accounts.api.v1.views.send_otp_email.delay')

    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        api_client.post(reverse('send-otp-login'), {'email': buyer_user.email})

    otp_record = OTP.objects.filter(user=buyer_user).latest('created_at')
    otp_record.set_otp(otp)
    otp_record.used_at = timezone.now()
    otp_record.save()

    data = {'email': buyer_user.email, 'otp': otp}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data


@pytest.mark.django_db
def test_verify_otp_missing_fields(api_client):
    url = reverse('verify-otp-login')
    data = {'email': 'buyer@example.com'}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'otp' in response.data


@pytest.mark.django_db
def test_verify_otp_nonexistent_user(api_client):
    url = reverse('verify-otp-login')
    data = {'email': 'nonexistent@example.com', 'otp': '123456'}

    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data
    assert response.data['non_field_errors'][0] == 'User does not exist.'


@pytest.mark.django_db
def test_verify_otp_throttling(api_client, buyer_user, mocker):
    url = reverse('verify-otp-login')
    otp = '123456'
    mocker.patch('accounts.api.v1.views.generate_otp', return_value=otp)
    mocker.patch('accounts.api.v1.views.send_otp_email.delay')

    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {}}):
        api_client.post(reverse('send-otp-login'), {'email': buyer_user.email})

    otp_record = OTP.objects.filter(user=buyer_user).latest('created_at')
    otp_record.set_otp(otp)
    otp_record.save()

    data = {'email': buyer_user.email, 'otp': 'wrongotp'}
    for _ in range(5):
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_logout_success(api_client, buyer_user, valid_refresh_token):
    api_client.force_authenticate(user=buyer_user)

    response = api_client.post('/accounts/api/v1/logout/', {'refresh_token': valid_refresh_token})
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_missing_refresh_token(auth_client):
    url = reverse('logout')
    data = {}

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data


@pytest.mark.django_db
def test_logout_invalid_refresh_token(auth_client):
    url = reverse('logout')
    data = {'refresh_token': 'invalidtoken'}

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data


@pytest.mark.django_db
def test_logout_blacklisted_token(auth_client, buyer_user):
    url = reverse('logout')
    refresh = RefreshToken.for_user(buyer_user)
    refresh.blacklist()

    data = {'refresh_token': str(refresh)}
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data


@pytest.mark.django_db
def test_logout_unauthenticated(api_client):
    url = reverse('logout')
    data = {'refresh_token': 'sometoken'}

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_password_reset_success(auth_client, buyer_user, mocker):
    url = reverse('password-reset')
    mock_send_email = mocker.patch('accounts.api.v1.views.send_password_reset_email.delay')

    data = {'email': buyer_user.email}
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Password reset email sent."
    mock_send_email.assert_called_once()


@pytest.mark.django_db
def test_password_reset_nonexistent_email(auth_client):
    url = reverse('password-reset')
    data = {'email': 'nonexistent@example.com'}

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_password_reset_missing_email(auth_client):
    url = reverse('password-reset')
    data = {}

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
def test_password_reset_confirm_success(api_client, buyer_user):
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = default_token_generator.make_token(buyer_user)
    url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

    data = {
        'uidb64': uid,
        'token': token,
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Password has been reset successfully."
    buyer_user.refresh_from_db()
    assert buyer_user.check_password('NewPassword@123')


@pytest.mark.django_db
def test_password_reset_confirm_invalid_uid(api_client):
    uid = 'invaliduid'
    token = 'sometoken'
    url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

    data = {
        'uidb64': uid,
        'token': token,
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'uidb64' in response.data


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(api_client, buyer_user):
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = 'invalidtoken'
    url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

    data = {
        'uidb64': uid,
        'token': token,
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'token' in response.data


@pytest.mark.django_db
def test_password_reset_confirm_passwords_do_not_match(api_client, buyer_user):
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = default_token_generator.make_token(buyer_user)
    url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

    data = {
        'uidb64': uid,
        'token': token,
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'DifferentPassword@123'
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'new_password_confirm' in response.data


@pytest.mark.django_db
def test_password_reset_confirm_missing_fields(api_client, buyer_user):
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = default_token_generator.make_token(buyer_user)
    url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})

    data = {
        'uidb64': uid,
        'token': token,
        'new_password_confirm': 'NewPassword@123'
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'new_password' in response.data


@pytest.mark.django_db
def test_change_password_success(auth_client, buyer_user):
    url = reverse('change-password')
    data = {
        'old_password': '1234QWas@#',
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }

    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Password changed successfully'
    buyer_user.refresh_from_db()
    assert buyer_user.check_password('NewPassword@123')


@pytest.mark.django_db
def test_change_password_incorrect_old_password(auth_client):
    url = reverse('change-password')
    data = {
        'old_password': 'wrongpassword',
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }

    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'old_password' in response.data


@pytest.mark.django_db
def test_change_password_mismatch_new_password(auth_client):
    url = reverse('change-password')
    data = {
        'old_password': '1234QWas@#',
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'DifferentPassword@123'
    }

    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'new_password_confirm' in response.data
    error_messages = response.data['new_password_confirm']
    assert error_messages == ['The new passwords do not match.']


@pytest.mark.django_db
def test_change_password_missing_fields(auth_client):
    url = reverse('change-password')
    data = {
        'old_password': '1234QWas@#',
        # 'new_password' and 'new_password_confirm' are missing
    }

    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'new_password' in response.data
    assert 'new_password_confirm' in response.data


@pytest.mark.django_db
def test_change_password_unauthenticated(api_client):
    url = reverse('change-password')
    data = {
        'old_password': '1234QWas@#',
        'new_password': 'NewPassword@123',
        'new_password_confirm': 'NewPassword@123'
    }

    response = api_client.put(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_account_success(auth_client, buyer_user):
    url = reverse('delete-account')
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Account deleted successfully'
    with pytest.raises(User.DoesNotExist):
        buyer_user.refresh_from_db()


@pytest.mark.django_db
def test_delete_account_unauthenticated(api_client):
    url = reverse('delete-account')
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_verify_email_success(auth_client, buyer_user, mocker):
    url = reverse('verify-email')
    mock_send_email = mocker.patch('accounts.api.v1.views.send_verification_email.delay')

    response = auth_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Verification email sent."
    mock_send_email.assert_called_once()


@pytest.mark.django_db
def test_verify_email_no_email(auth_client, create_user):
    user = create_user(email='test@example.com', password='password123', user_type=User.UserType.BUYER)

    user.email = ''
    user.save()

    auth_client.force_authenticate(user=user)
    url = reverse('verify-email')

    response = auth_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "No email associated with this account."


@pytest.mark.django_db
def test_verify_email_unauthenticated(api_client):
    url = reverse('verify-email')
    response = api_client.post(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_verify_email_success(api_client, buyer_user):
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = default_token_generator.make_token(buyer_user)
    url = reverse('verify-email-confirm', kwargs={'uidb64': uid, 'token': token})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Email verified successfully."
    buyer_user.refresh_from_db()
    assert buyer_user.email_verified is True


@pytest.mark.django_db
def test_verify_email_invalid_uid(api_client):
    uid = 'invaliduid'
    token = 'sometoken'
    url = reverse('verify-email-confirm', kwargs={'uidb64': uid, 'token': token})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Invalid verification link or token."


@pytest.mark.django_db
def test_verify_email_invalid_token(api_client, buyer_user):
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = 'invalidtoken'
    url = reverse('verify-email-confirm', kwargs={'uidb64': uid, 'token': token})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Invalid verification link or token."


@pytest.mark.django_db
def test_verify_email_already_verified(api_client, buyer_user):
    buyer_user.email_verified = True
    buyer_user.save()
    uid = urlsafe_base64_encode(force_bytes(buyer_user.pk))
    token = default_token_generator.make_token(buyer_user)
    url = reverse('verify-email-confirm', kwargs={'uidb64': uid, 'token': token})

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == "Email verified successfully."
