# SessionHistoryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sessions** | [**List[SessionHistoryItem]**](SessionHistoryItem.md) |  | 
**total_sessions** | **int** |  | 
**finished_sessions** | **int** |  | 
**completed_sessions** | **int** |  | 
**completion_ratio** | **float** |  | 

## Example

```python
from deepwork_sdk.models.session_history_response import SessionHistoryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SessionHistoryResponse from a JSON string
session_history_response_instance = SessionHistoryResponse.from_json(json)
# print the JSON string representation of the object
print(SessionHistoryResponse.to_json())

# convert the object into a dict
session_history_response_dict = session_history_response_instance.to_dict()
# create an instance of SessionHistoryResponse from a dict
session_history_response_from_dict = SessionHistoryResponse.from_dict(session_history_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


