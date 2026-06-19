from query import query_rag_pipeline

def main():
    print("\n🤖 Welcome to the Document Q&A Bot!")
    print("Type 'quit' or 'exit' to stop the chat.")
    print("-" * 50)

    while True:
        # 1. Wait for the user to type a question
        user_question = input("\nQuestion: ")
        
        # 2. Check if they want to leave
        if user_question.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        # 3. Ignore empty questions
        if not user_question.strip():
            continue
            
        print("Searching documents...\n")
        
        # 4. Call your pipeline!
        try:
            result = query_rag_pipeline(user_question)
            
            print("--- AI ANSWER ---")
            print(result["answer"])
            
            print("\n--- SOURCES USED ---")
            # We use 'set' here to remove duplicate citations if it pulled multiple chunks from the exact same page
            unique_citations = set(result["citations"])
            for citation in unique_citations:
                print(f"- {citation}")
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()