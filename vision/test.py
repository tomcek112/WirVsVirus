from Camera import Camera
c = Camera("123", "178.15.51.243:80")
from Viewer import Viewer
v = Viewer(c)
print(v.createObservation())