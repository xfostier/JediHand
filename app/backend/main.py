import mediapipe as mp
import cv2
import backend.modules.detection as dt
import backend.styles.styles as styles
import backend.modules.actionselector as a_s

mp_drawing = mp.solutions.drawing_utils
#mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def stream():
  # For webcam input:
  cap = cv2.VideoCapture(0)
  with mp_hands.Hands(
      model_complexity=0,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      raisedfingers = dt.process_image(image)
      a_s.select(raisedfingers)
      results = hands.process(image)

      # Draw the hand annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
          mp_drawing.draw_landmarks(
              image,
              hand_landmarks,
              mp_hands.HAND_CONNECTIONS,
              #mp_drawing_styles.get_default_hand_landmarks_style(),
              styles.get_default_hand_landmarks_style(),
              #mp_drawing_styles.get_default_hand_connections_style())
              styles.get_default_hand_connections_style())
      # Flip the image horizontally for a selfie-view display.
      image = cv2.flip(image, 1)
      image_height, image_width, _ = image.shape
      textcoord = (image_width - 200, image_height - 60)
      cv2.putText(image,str(raisedfingers),textcoord,cv2.FONT_HERSHEY_PLAIN,20,(255,255,255),20)  
      #cv2.imshow('MediaPipe Hands',image)
      ret, buffer = cv2.imencode('.jpg', image)
      image = buffer.tobytes()
      yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')  # concat frame one by one and show result
        
      if cv2.waitKey(5) & 0xFF == 27:
        break
  cap.release()