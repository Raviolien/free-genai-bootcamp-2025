import chromadb
from chromadb.config import Settings
from pathlib import Path
import json
import hashlib

class ExerciseVectorStore:
    def __init__(self, persist_dir: str = "vector_db"):
        """
        Initialize the vector store for exercises
        
        Args:
            persist_dir (str): Directory to persist the vector database
        """
        self.persist_dir = Path(__file__).parent / persist_dir
        self.persist_dir.mkdir(exist_ok=True)
        
        # Initialize ChromaDB with sentence-transformers embedding function
        self.client = chromadb.Client(Settings(
            persist_directory=str(self.persist_dir),
            is_persistent=True,
            anonymized_telemetry=False
        ))
        
        # Create collections with embedding function
        embedding_function = chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # You can choose different models based on your needs
        )
        
        self.multiple_choice = self.client.get_or_create_collection(
            "multiple_choice",
            embedding_function=embedding_function
        )
        self.dialog_matching = self.client.get_or_create_collection(
            "dialog_matching",
            embedding_function=embedding_function
        )
        self.other_exercises = self.client.get_or_create_collection(
            "other_exercises",
            embedding_function=embedding_function
        )

    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for an exercise based on its content"""
        return hashlib.md5(content.encode()).hexdigest()

    def add_exercises(self, exercises_dir: Path) -> None:
        """
        Add exercises from the exercises directory to the vector store
        
        Args:
            exercises_dir (Path): Path to exercises directory
        """
        # Process multiple choice exercises
        for mc_file in exercises_dir.glob("*_multiple_choice.txt"):
            video_id = mc_file.stem.replace("_multiple_choice", "")
            
            with open(mc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                exercises = self._parse_multiple_choice(content)
                for exercise in exercises:
                    exercise_id = self._generate_id(str(exercise))
                    # Create embeddings from the content and questions
                    embedding_text = exercise['content'] + ' ' + ' '.join(
                        [q['question'] + ' ' + ' '.join(q['options']) 
                         for q in exercise['questions']]
                    )
                    self.multiple_choice.upsert(
                        ids=[exercise_id],
                        documents=[embedding_text],  # Text to create embeddings from
                        metadatas=[{
                            "video_id": video_id,
                            "type": "multiple_choice",
                            "full_exercise": json.dumps(exercise)
                        }]
                    )

        # Process dialog matching exercises
        for dm_file in exercises_dir.glob("*_dialog_matching.txt"):
            video_id = dm_file.stem.replace("_dialog_matching", "")
            
            with open(dm_file, 'r', encoding='utf-8') as f:
                content = f.read()
                exercise = self._parse_dialog_matching(content)
                if exercise:
                    exercise_id = self._generate_id(str(exercise))
                    # Create embeddings from the dialogs
                    embedding_text = ' '.join(exercise['dialogs'])
                    self.dialog_matching.upsert(
                        ids=[exercise_id],
                        documents=[embedding_text],  # Text to create embeddings from
                        metadatas=[{
                            "video_id": video_id,
                            "type": "dialog_matching",
                            "full_exercise": json.dumps(exercise)
                        }]
                    )

        # Process other exercises
        for other_file in exercises_dir.glob("*_other_exercises.txt"):
            video_id = other_file.stem.replace("_other_exercises", "")
            
            with open(other_file, 'r', encoding='utf-8') as f:
                content = f.read()
                exercise = self._parse_other_exercise(content)
                if exercise:
                    exercise_id = self._generate_id(str(exercise))
                    # Create embeddings from the content
                    embedding_text = exercise.get('content', '')
                    self.other_exercises.upsert(
                        ids=[exercise_id],
                        documents=[embedding_text],  # Text to create embeddings from
                        metadatas=[{
                            "video_id": video_id,
                            "type": exercise.get("type", "unknown"),
                            "full_exercise": json.dumps(exercise)
                        }]
                    )

    def _parse_multiple_choice(self, content: str) -> list:
        """Parse multiple choice exercise content into structured format"""
        exercises = []
        current_exercise = None
        current_question = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Content:'):
                if current_exercise:
                    exercises.append(current_exercise)
                current_exercise = {
                    'content': line.replace('Content:', '').strip(),
                    'questions': []
                }
            elif line.startswith('Question:'):
                if current_question and current_exercise:
                    current_exercise['questions'].append(current_question)
                current_question = {
                    'question': line.replace('Question:', '').strip(),
                    'options': [],
                    'correct_answer': None
                }
            elif line.startswith('- '):
                if current_question:
                    current_question['options'].append(line.replace('- ', '').strip())
            elif line.startswith('Correct answer:'):
                if current_question:
                    current_question['correct_answer'] = line.replace('Correct answer:', '').strip()
                    current_exercise['questions'].append(current_question)
                    current_question = None

        if current_exercise:
            exercises.append(current_exercise)
        
        return exercises

    def _parse_dialog_matching(self, content: str) -> dict:
        """Parse dialog matching exercise content into structured format"""
        dialogs = []
        images = []
        correct_matches = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line == 'Dialogs:':
                current_section = 'dialogs'
            elif line == 'Images:':
                current_section = 'images'
            elif line == 'Correct matches:':
                current_section = 'matches'
            elif line.startswith('- '):
                if current_section == 'dialogs':
                    dialogs.append(line.replace('- ', '').strip())
                elif current_section == 'images':
                    images.append(line.replace('- ', '').strip())
            elif line.startswith('Dialog:'):
                dialog = line.replace('Dialog:', '').strip()
            elif line.startswith('Matches with:'):
                image = line.replace('Matches with:', '').strip()
                correct_matches[dialog] = image

        return {
            'dialogs': dialogs,
            'images': images,
            'correct_matches': correct_matches
        }

    def _parse_other_exercise(self, content: str) -> dict:
        """Parse other exercise content into structured format"""
        exercise = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Content:'):
                exercise['content'] = line.replace('Content:', '').strip()
            elif line.startswith('Type:'):
                exercise['type'] = line.replace('Type:', '').strip()
            elif line.startswith('Solution:'):
                exercise['solution'] = line.replace('Solution:', '').strip()
            
        return exercise

    def query_similar_exercises(self, query: str, exercise_type: str, n_results: int = 5) -> list:
        """
        Query for similar exercises using semantic search
        
        Args:
            query (str): Query text
            exercise_type (str): Type of exercise to query ("multiple_choice", "dialog_matching", or "other")
            n_results (int): Number of results to return
            
        Returns:
            list: List of similar exercises
        """
        collection = getattr(self, exercise_type, None)
        if not collection:
            raise ValueError(f"Invalid exercise type: {exercise_type}")

        # Get collection size
        collection_size = collection.count()
        # Adjust n_results if needed
        n_results = min(n_results, collection_size)

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Parse exercises from metadata
        exercises = []
        for metadata in results['metadatas'][0]:
            try:
                exercise = json.loads(metadata['full_exercise'])
                exercises.append(exercise)
            except (json.JSONDecodeError, KeyError):
                continue

        return exercises

    def get_exercise_by_id(self, exercise_id: str, exercise_type: str) -> dict:
        """
        Get a specific exercise by ID
        
        Args:
            exercise_id (str): Exercise ID
            exercise_type (str): Type of exercise
            
        Returns:
            dict: Exercise data
        """
        collection = getattr(self, exercise_type, None)
        if not collection:
            raise ValueError(f"Invalid exercise type: {exercise_type}")

        result = collection.get(ids=[exercise_id])
        
        if result['documents']:
            try:
                return json.loads(result['documents'][0])
            except json.JSONDecodeError:
                return None
        return None

if __name__ == "__main__":
    # Example usage
    store = ExerciseVectorStore()
    
    # Add exercises from the exercises directory
    exercises_dir = Path(__file__).parent / "data" / "exercises"
    store.add_exercises(exercises_dir)
    
    # Example query for dialog matching
    print("\nQuerying dialog matching exercises:")
    query = "dialogue about ordering food in a restaurant"
    results = store.query_similar_exercises(query, "dialog_matching")
    for result in results:
        print(f"\nDialogs: {result.get('dialogs', [])}")
        print(f"Images: {result.get('images', [])}")

    # Example query for multiple choice
    print("\nQuerying multiple choice exercises:")
    query = "questions about train departure times and platforms"
    results = store.query_similar_exercises(query, "multiple_choice")
    for result in results:
        print(f"\nContent: {result.get('content', '')}")
        print("Questions:")
        for question in result.get('questions', []):
            print(f"  - {question.get('question', '')}")
            print(f"    Options: {question.get('options', [])}")
            print(f"    Correct answer: {question.get('correct_answer', '')}") 