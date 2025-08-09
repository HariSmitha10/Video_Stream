# Video Stream UI

Lightweight MJPEG streaming interface for Raspberry Pi.

## Raspberry Pi Setup (Video Source)
Run on Pi:
```bash
docker run -d \
  --name=mjpg-streamer \
  --restart=always \
  --device=/dev/video0:/dev/video0 \
  -p 8080:8080 \
  -e MJPEG_STREAMER_INPUT="-y -n -r 1280x720 -f 30" \
  patsoffice/mjpg-streamer

