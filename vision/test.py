from Camera import Camera
c = Camera("123", "82.65.5.211:8082")
from Viewer import Viewer
v = Viewer(c, "asd", "asd")
v.run()