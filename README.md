# Fast Api

## Python based API backend for the project

To run this project

1. Install the required packages by running `pip install -r requirements.txt` in your terminal
2. Run the project by running in the format like
   `python -m uvicorn File_name:object_name --reload` or `uvicorn File_name:object_name --reload`

   ```bash
   uvicorn main:app --reload
   ```

   Or

   ```bash
   python -m uvicorn main:app --reload
   ```

   in your terminal

3. Open a new terminal and run `curl http://127.0.0.1:8000`
