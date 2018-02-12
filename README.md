#openLPC

## open License Plate Censoring

openLPC is a tool based on openALPR and openCV to detect license plates and censoring them using gaussian blurring.

## Usage

### Modes

**There are three different modes (atm)**:

`image`: censors a single image (provided by -path)
`imagestack`: censors every image inside a given folder (provided by -path)
`video`: censors a video file (provided by -path). To create a videofile as output pass `-output video` as argument

### Arguments

```
  -h, --help                show this help message and exit
  -size MATRIX_SIZE         Size of the matrix
  -multiplier MULTIPLIER    Image/Frame mulitplied by given value
  -path FILEPATH            path to the file (for imagestack: path to the folder)
  -mode MODE                mode (image, imagestack, video)
  -output OUTPUT            output format (video, image)
  -show                     Display the output (screen required)
  -debug                    Debug mode (pink bar instead of blurred plate)
```

### Licence

[AGPL](http://www.gnu.org/licenses/agpl-3.0.html)
