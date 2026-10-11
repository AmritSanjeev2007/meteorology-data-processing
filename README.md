# Meteorological Data Processing

A data processing python project for processing global mean temperature data. There is already sample temperature data for May 2026. The data was projected onto a highly detailed sphere. The sphere itself was generated using a fragment shader and OpenGL. The sphere also shows the current day-night lighting.  

<img width="3078" height="2136" alt="image" src="https://github.com/user-attachments/assets/28fc53d8-5ccd-48b7-8315-90c4d66bf49f" />

After downloading this repo, execute the following commands in the downloaded repo directory (assuming the required version of python is available on the host machine).

```bash
python -m venv .venv
python install -r requirements.txt
```

And then voila, you can open up the display window by running:

```bash
python main.py
```

**Note that this will only work on a PC since the program has been designed with only PCs in mind.**
