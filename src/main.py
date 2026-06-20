from query import query_rag_pipeline

def main():
    print("\n🤖 Welcome to the Document Q&A Bot!")
    print("Type 'quit' or 'exit' to stop the chat.")
    print("-" * 50)

    while True:
        user_question = input("\nQuestion: ")
        
        if user_question.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
            
        if not user_question.strip():
            continue
            
        print("Searching documents...\n")
        try:
            result = query_rag_pipeline(user_question)
            
            print("--- AI ANSWER ---")
            print(result["answer"])
            
            print("\n--- SOURCES USED ---")
            unique_citations = set(result["citations"])
            for citation in unique_citations:
                print(f"- {citation}")
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()