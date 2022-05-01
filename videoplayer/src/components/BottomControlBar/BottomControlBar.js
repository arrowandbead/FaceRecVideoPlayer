import React, { Component } from "react";
import Slider from '@material-ui/core/Slider';
import FullscreenIcon from '@material-ui/icons/Fullscreen';


class BottomControlBar extends Component {

    formatSeconds(d) {
        var h = Math.floor(d / 3600);
        var m = Math.floor(d % 3600 / 60);
        var s = Math.floor(d % 3600 % 60);
      
        const a = [h,m,s]
        const displayVal = a.join(':')
        return <div className="timeSliderLabel">{displayVal}</div>
      }
    
    

    render() {
        return(
            <div className='bottomControlBar'>
                  <div className="timeControlsHolder">
                    <div className='sliderHolder'>
                      <Slider className="timeControlSlider"
                      min={0}
                      max={this.props.videoLengthSeconds}
                      value={this.props.progress}
                      valueLabelFormat={(value) => this.formatSeconds(value) }
                      valueLabelDisplay="on"
                      onChangeCommitted={this.props.setVidTime}>

                      </Slider>
                    </div>
                  </div>
                  <div className = 'otherControlsHolder'>
                    <button className="buttonStyle playPauseButton" onClick={this.props.pauseUnpause}>
                      {this.props.deliverPlayPauseIconBottomBar()}
                    </button>
                    <div className='volHolder'>
                      <button className="buttonStyle" onClick={this.props.muteUnmute}>
                        {this.props.deliverVolumeIcon()}
                      </button>
                      <div className='volSliderHolder'>
                        <Slider 
                        min={0}
                        max={100}
                        defaultValue={0}
                        className="volSlider"
                        onChange={(e, value) => this.props.setVolume(value)}>
    
                        </Slider>
                      </div>
                    </div>
                    <div className="fullScreenButtonHolder">
                        <button className = "fullScreenButton buttonStyle" onClick={this.props.toggleFullScreen}>
                          <FullscreenIcon></FullscreenIcon>
                        </button>
                      </div>
                  </div>
                </div>
        )
    }
}

export default BottomControlBar