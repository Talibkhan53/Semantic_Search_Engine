from pathlib import Path

class Loader:
    def file_loads(self,path:Path):
     path = Path(path)

     file_data = {}
     if path.is_file():
        with open(path,'r') as current_file:
           file_data[path.name] = current_file.read().strip()

     elif path.is_dir():
        files = [
           f for f in path.iterdir()
           if f.is_file()
        ]

        for file in files:
           with open(file,'r') as current_file:
              file_data[file.name] = current_file.read().strip()
     return file_data
      



      
        