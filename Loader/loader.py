from pathlib import Path

class Loader:
    def file_loads(self,directory_path:Path):
  
    #   Get only files in this immediate directory
      files =  [ f for f in directory_path.iterdir() if f.is_file()]

    # Another Way of Writing Above Line
    #   files = []
    #   for f in directory_path.iterdir():
    #      if f.is_file():
    #         files.append(f)  
      file_data = {}
      for f in files:
        with open(f,'r') as current_file :
          file_data[f.name] =  current_file.read().strip()
      return file_data