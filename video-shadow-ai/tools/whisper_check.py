import sherpa_onnx, soundfile as sf, sys, numpy as np, subprocess
m="/opt/models/sherpa-onnx-whisper-small/small-"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=m+"encoder.onnx",decoder=m+"decoder.onnx",tokens=m+"tokens.txt",language="it",task="transcribe",num_threads=4)
for f in sys.argv[1:]:
    raw=subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.float32)
    s=rec.create_stream(); s.accept_waveform(16000,a); rec.decode_stream(s); print(f.split('/')[-1], "->", s.result.text)
