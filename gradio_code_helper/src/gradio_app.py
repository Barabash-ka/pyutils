import gradio as gr

#--------------------------------------#
import numpy as np
def sepia(input_img):
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = input_img.dot(sepia_filter.T)
    sepia_img /= sepia_img.max()
    return sepia_img
sepia_demo = gr.Interface(sepia, gr.Image(), "image")

#--------------------------------------#
def greet(name, age):
    return "Hello, " + name + "!" * int(age)
greet_demo = gr.Interface(
    fn=greet,
    inputs=[gr.Textbox(label="Enter your name"), gr.Slider(label="Enter your age", value=18, minimum=18, maximum=120, step=1)],
    outputs=[gr.Textbox(label="Here is your greeting", lines=3)],
    # inputs=["text", "slider"],
    # outputs=["text"],
)

#--------------------------------------#
def flip(im):
    # return np.flipud(im)
    return np.fliplr(im)

webcam_demo = gr.Interface(
    flip,
    gr.Image(sources=["webcam"], streaming=True),
    "image",
    live=True
)
# demo.launch(share=True)

# demo = greet_demo
# demo = sepia_demo
demo = webcam_demo

if __name__ == "__main__":
    demo.launch()
