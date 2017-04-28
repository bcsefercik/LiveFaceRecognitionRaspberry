import cognitive_face as CF

KEY = '3686dfd949a64b1ead4bf46862683dc4'  # Replace with a valid Subscription Key here.
CF.Key.set(KEY)

img_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
data = open('/home/bcsefercik/Desktop/ELEC491/data/bugra/face10.jpg', 'rb')
result = CF.face.detect(data)
print result