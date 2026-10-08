# deepwork_sdk.SessionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**complete_session**](SessionsApi.md#complete_session) | **PATCH** /sessions/{session_id}/complete | Complete Session
[**create_session**](SessionsApi.md#create_session) | **POST** /sessions/ | Create Session
[**get_session_history**](SessionsApi.md#get_session_history) | **GET** /sessions/history | Get Session History
[**pause_session**](SessionsApi.md#pause_session) | **PATCH** /sessions/{session_id}/pause | Pause Session
[**resume_session**](SessionsApi.md#resume_session) | **PATCH** /sessions/{session_id}/resume | Resume Session
[**start_session**](SessionsApi.md#start_session) | **PATCH** /sessions/{session_id}/start | Start Session


# **complete_session**
> SessionResponse complete_session(session_id)

Complete Session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_response import SessionResponse
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Complete Session
        api_response = api_instance.complete_session(session_id)
        print("The response of SessionsApi->complete_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->complete_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Session is not active |  -  |
**503** | Database operation failed |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_session**
> SessionResponse create_session(session_create)

Create Session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_create import SessionCreate
from deepwork_sdk.models.session_response import SessionResponse
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_create = deepwork_sdk.SessionCreate() # SessionCreate | 

    try:
        # Create Session
        api_response = api_instance.create_session(session_create)
        print("The response of SessionsApi->create_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->create_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_create** | [**SessionCreate**](SessionCreate.md)|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_session_history**
> SessionHistoryResponse get_session_history()

Get Session History

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_history_response import SessionHistoryResponse
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.SessionsApi(api_client)

    try:
        # Get Session History
        api_response = api_instance.get_session_history()
        print("The response of SessionsApi->get_session_history:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->get_session_history: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**SessionHistoryResponse**](SessionHistoryResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **pause_session**
> SessionResponse pause_session(session_id, pause_request)

Pause Session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.pause_request import PauseRequest
from deepwork_sdk.models.session_response import SessionResponse
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 
    pause_request = deepwork_sdk.PauseRequest() # PauseRequest | 

    try:
        # Pause Session
        api_response = api_instance.pause_session(session_id, pause_request)
        print("The response of SessionsApi->pause_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->pause_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 
 **pause_request** | [**PauseRequest**](PauseRequest.md)|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Session is not active |  -  |
**503** | Database operation failed |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resume_session**
> SessionResponse resume_session(session_id)

Resume Session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_response import SessionResponse
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Resume Session
        api_response = api_instance.resume_session(session_id)
        print("The response of SessionsApi->resume_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->resume_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Session not found |  -  |
**409** | Session cannot be resumed |  -  |
**503** | Database operation failed |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_session**
> SessionResponse start_session(session_id)

Start Session

### Example


```python
import deepwork_sdk
from deepwork_sdk.models.session_response import SessionResponse
from deepwork_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = deepwork_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with deepwork_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = deepwork_sdk.SessionsApi(api_client)
    session_id = 56 # int | 

    try:
        # Start Session
        api_response = api_instance.start_session(session_id)
        print("The response of SessionsApi->start_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SessionsApi->start_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **int**|  | 

### Return type

[**SessionResponse**](SessionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

