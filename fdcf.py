from PIL import Image
import face_recognition
import os

# Load the jpg file into a numpy array
image = face_recognition.load_image_file("biden.jpg")

# Find all the faces in the image using the default HOG-based model.
face_locations = face_recognition.face_locations(image)

print("I found {} face(s) in this photograph.".format(len(face_locations)))

output_dir = "extracted_faces"
os.makedirs(output_dir, exist_ok=True)

for i, face_location in enumerate(face_locations):
    # Print the location of each face in this image
    top, right, bottom, left = face_location
    print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

    # Extract the face image from the original image
    face_image = image[top:bottom, left:right]
    
    # Convert the face image from numpy array to PIL Image
    pil_image = Image.fromarray(face_image)

    # Save the face image
    pil_image.save(os.path.join(output_dir, f"face_{i}.png"))
