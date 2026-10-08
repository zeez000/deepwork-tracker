from deepwork_sdk import ApiClient, Configuration
from deepwork_sdk.api.sessions_api import SessionsApi


def main():
    configuration = Configuration(host="http://127.0.0.1:8000")

    with ApiClient(configuration) as api_client:
        sessions_api = SessionsApi(api_client)
        history = sessions_api.get_session_history()

        print("SDK connected successfully!")
        print(f"Total sessions: {history.total_sessions}")
        print(f"Completed sessions: {history.completed_sessions}")

        for session in history.sessions:
            print(
                f"Session {session.id}: "
                f"{session.title} — {session.status}"
            )


if __name__ == "__main__":
    main()



