import streamlit as st
import requests, json


def get_database_list():
    endpoint = "http://api:80/fandom_wikis"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error related to request occurred: {e}"
    except Exception as e:
        return f"Unexpected exception has occurred: {e}"

    return [table["database_table_name"] for table in response.json()]


def process_input(input_text, selected_database):
    endpoint = "http://api:80/fandom_wikis/" + selected_database + "/contents/" + input_text

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error related to request occurred: {e}"
    except Exception as e:
        return f"Unexpected exception has occurred: {e}"

    return f"{response.text}"


def process_input_detailed(input_text, selected_database):
    endpoint = "http://api:80/fandom_wikis/" + selected_database + "/contents/" + input_text + "/p"

    try:
        response = requests.get(endpoint)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error related to request occurred: {e}"
    except Exception as e:
        return f"Unexpected exception has occurred: {e}"

    return f"{response.text}"


def main():
    st.set_page_config(page_title="Knowledge Extraction | Team MRKVA")
    st.title("Knowledge Extraction")
    st.header("Team MRKVA")

    st.subheader("Select database to search:")
    # Dropdown to select a database
    database_list = get_database_list()
    selected_database = st.selectbox("Select a database:", database_list)

    # Input field
    st.subheader("Enter keyword to filter data:")
    input_text = st.text_input("Enter keyword to filter data:", label_visibility="hidden")

    if st.button("Search database"):
        result = process_input(input_text, selected_database)

    if st.button("Get recommended result from database"):
        result = process_input_detailed(input_text, selected_database)

    st.subheader("Response:")
    st.json(result, expanded=False)


if __name__ == "__main__":
    main()
