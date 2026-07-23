import cv2
import sys

# Video input path
video_path = "utils/Einstein Final Tiebreaker - FIRST Championship - FIRST Robotics Competition.mp4"

# ==============================================================================
# SPEED & SKIP CONTROLS
# ==============================================================================
# INCREASED SKIP: Try increasing this to 300, 450, or 600 if 180 is still on an intro screen!
# At 30 FPS: 180 frames = 6s | 300 frames = 10s | 450 frames = 15s | 600 frames = 20s
FRAMES_TO_SKIP = 380

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def drawRectangle(frame, bbox):
    """Draws the bounding box tracking window onto the frame."""
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)

def drawText(frame, txt, location, color=(50, 170, 50)):
    cv2.putText(frame, txt, location, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

# ------------------------------------------------------------------------------
# Core Setup and Configuration
# ------------------------------------------------------------------------------
# SPEED & STABILITY ENGINE: MIL handles robot rotation and rapid movement
tracker = cv2.TrackerMIL_create()

# Open video file
video = cv2.VideoCapture(video_path)
if not video.isOpened():
    print(f"Error: Could not open video file at: {video_path}")
    sys.exit()

# Get video properties
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

# ==============================================================================
# EXECUTE CHOSEN FRAME JUMP
# ==============================================================================
if FRAMES_TO_SKIP > 0:
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    if FRAMES_TO_SKIP < total_frames:
        # Move the internal openCV reader index ahead
        video.set(cv2.CAP_PROP_POS_FRAMES, FRAMES_TO_SKIP)
        print(f"Successfully skipped ahead {FRAMES_TO_SKIP} frames (~{round(FRAMES_TO_SKIP/fps, 1)} seconds).")
    else:
        print("Warning: Skipped frame count exceeds total video duration. Starting from frame 0.")

# Read the starting frame after skipping
ok, frame = video.read()
if not ok:
    print("Error: Could not read the starting frame after skipping.")
    video.release()
    sys.exit()

# Get the exact index we successfully landed on
current_frame_index = int(video.get(cv2.CAP_PROP_POS_FRAMES))
print(f"Opening selection tool using Frame Index: {current_frame_index}")

# Configure output video writer
video_output_file_name = "modified.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_out = cv2.VideoWriter(video_output_file_name, fourcc, fps, (width, height))

# ==============================================================================
# INTERACTIVE MOUSE SELECTION (FIXES FIXED MATH BOUNDING BOX FAILURES)
# ==============================================================================
print("\n--- ACTION REQUIRED ---")
print("1. A window named 'Select Target Object' has opened.")
print("2. Use your mouse to CLICK and DRAG a box around the robot you want to track.")
print("3. Press ENTER or SPACEBAR on your keyboard to confirm and begin tracking.")
print("------------------------\n")

# This opens a window letting you precisely target your robot
bbox = cv2.selectROI("Select Target Object", frame, fromCenter=False, showCrosshair=True)
cv2.destroyWindow("Select Target Object")

# If you closed the window without drawing a box, fallback to your math formulas
if bbox[2] == 0 or bbox[3] == 0:
    print("No custom box selected. Falling back to mathematical fraction coordinates...")
    frac1 = int((235.0 / 1871.0) * width)
    frac2 = int((372.0 / 1871.0) * width)
    frac3 = int((435.0 / 1014.0) * height)
    frac4 = int((335.0 / 1014.0) * height)
    bbox = (frac1, frac3, frac2, frac4)

# Initialize the tracking engine with your chosen box boundaries
ok = tracker.init(frame, bbox)

# Write the initialized first frame to the output stream
video_out.write(frame)

# ------------------------------------------------------------------------------
# Main Processing Video Loop
# ------------------------------------------------------------------------------
print("Processing tracking video... Press 'q' inside the preview to stop early.")

bbox_list = []

while True:
    ok, frame = video.read()
    if not ok:
        break  # End of video reached

    # Update tracker location mapping
    tracking_ok, bbox = tracker.update(frame)

    current_frame = video.get(cv2.CAP_PROP_POS_FRAMES)

    # 2. Divide current frame by the video FPS to get total elapsed seconds
    elapsed_seconds = (current_frame / fps) - (FRAMES_TO_SKIP/fps)

    # 3. Format seconds into clean, legible Minutes:Seconds strings

    seconds = int(elapsed_seconds)
    time_string = f"Time: {seconds:02d} (Frame: {current_frame})"

    # Render tracking boundary box or error text
    if tracking_ok:
        drawRectangle(frame, bbox)
        bbox_list.append((bbox, elapsed_seconds))
    else:
        drawText(frame, "tracking failed", (80, 140), (0, 0, 255))

    # Commit processed frame into the saved video file
    video_out.write(frame)

    # Live preview playback
    cv2.imshow("Live Tracking Preview", frame)

    # 1ms delay for optimized computing execution speeds
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Processing interrupted early by user.")
        break

# Cleanup
video.release()
video_out.release()
cv2.destroyAllWindows()
print(f"Success! Complete processed tracking video saved to: {video_output_file_name}")

for bbox in bbox_list:
    x1,y1,x2,y2 = bbox[0]
    print(f"Bounding Box at {bbox[1]}: {x1},{y1},{x2},{y2}")


