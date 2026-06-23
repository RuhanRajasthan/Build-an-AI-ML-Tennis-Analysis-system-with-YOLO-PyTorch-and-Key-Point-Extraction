from roboflow import Roboflow
rf = Roboflow(api_key="TYX8CK6LtI8UX8FEN6jI")
project = rf.workspace("viren-dhanwani").project("tennis-ball-detection")
version = project.version(6)
dataset = version.download("yolo26")
                