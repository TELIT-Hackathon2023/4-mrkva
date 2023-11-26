import streamlit as st

def process_input(input_text):
    # You can perform processing on the input text here
    # For simplicity, just echoing the input in this example
    return f"You entered: {input_text}"

def main():
    st.title("Simple Streamlit App")

    # Input field
    input_text = st.text_input("Enter text:")

    # Button to trigger the processing
    if st.button("Process"):
        # Process the input when the button is clicked
        result = process_input(input_text)

        # Display the result in the response field
        st.text_area("Response:", result)


if __name__ == "__main__":
    main()