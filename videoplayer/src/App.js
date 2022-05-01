import './App.css';
import React, { Component } from "react";
import ReactPlayer from 'react-player';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import {Typography } from '@material-ui/core';
import PlayArrowIcon from '@material-ui/icons/PlayArrow'
import PauseIcon from '@material-ui/icons/Pause'
import Tooltip from '@material-ui/core/Tooltip';
import VolumeUpIcon  from '@material-ui/icons/VolumeUp'
import VolumeMuteIcon  from '@material-ui/icons/VolumeMute'
import screenfull from 'screenfull';
import BottomControlBar from './components/BottomControlBar/BottomControlBar';
import stuff from "./hi.js"
// "https://vimeo.com/389022114"
const listV = stuff["content"].split("$")
let mapthing = {}
for (var i =0; i < listV.length; i++){
  let huh = listV[i]
  let SplitHuh = huh.split(',')
  let frame = parseInt(SplitHuh[0])
  let itemList = []
  for (var j =1; j < 5; j++){
    itemList.push(parseInt(SplitHuh[j]))
  }
  if(mapthing[frame] !== undefined){
    mapthing[frame].push(itemList)
  } else {
    mapthing[frame] = [itemList,]
  }
}
// console.log(mapthing)

class App extends Component {

  constructor(props) {
    super(props)
    this.state = {
      playing : false,
      videoLengthSeconds : 600,
      progress : 0,
      volume : 0,
      muted : false,
      playerContainerRef : null,
      visibleControls : false,
      fullscreen : false,
      timeout : null,
      x : 0,
      y : 0,
      progFractionForFaces : 0,
      currBBoxInfo : undefined,
      visibleBoundingBox : "",
      aBBOXIsVisible : false
    }

    this.timeoutHack = setTimeout(function(){}, 1000)
    this.hackyTimeoutIncrement = 0
    this.standardHeightWidthRatio = (360.0/640.0)
   
    this.pauseUnpause = this.pauseUnpause.bind(this)
    this.deliverPlayPauseIcon = this.deliverPlayPauseIcon.bind(this)
    this.deliverPlayPauseIconBottomBar = this.deliverPlayPauseIconBottomBar.bind(this)
    this.setVidTime = this.setVidTime.bind(this)
    this.deliverVolumeIcon = this.deliverVolumeIcon.bind(this)
    this.setStateVidDuration = this.setStateVidDuration.bind(this)
    this.getVolume = this.getVolume.bind(this)
    this.handleProgress = this.handleProgress.bind(this)
    this.hackyTimeoutAdder = this.hackyTimeoutAdder.bind(this)
    this.faceBoundingBoxes = this.faceBoundingBoxes.bind(this)
    this.pause = this.pause.bind(this)
    this.mouseExitPlayer = this.mouseExitPlayer.bind(this)
    
  }

  handleProgress(stuff){
    clearTimeout(this.timeoutHack)
    const boxInfo = mapthing[Math.round(stuff.played * 150289)]

    this.setState({
      progress : Math.round(stuff.playedSeconds),
      progFractionForFaces : stuff.played,
      currBBoxInfo : boxInfo,
    })
    this.hackyTimeoutAdder()
  }

  hackyTimeoutAdder(){
    clearTimeout(this.timeoutHack)
    if (this.state.playing){
      this.timeoutHack = setTimeout(this.hackyTimeoutAdder, 33)
    }

    const boxInfo = mapthing[Math.round((this.state.progFractionForFaces + this.hackyTimeoutIncrement) * 150289)]
  
    this.setState({
      progFractionForFaces : this.state.progFractionForFaces + this.hackyTimeoutIncrement,
      currBBoxInfo : boxInfo,
    })
    // console.log(this.state.progFractionForFaces)
    // console.log(Math.round(this.state.progFractionForFaces * 150289))
  }


  _onMouseMove(e) {
   

    const playerRect = this.playerContainerRef.getBoundingClientRect()

    let x = e.pageX - playerRect.x
    let y = e.pageY - playerRect.y

   


    if (this.state.currBBoxInfo !== undefined  ||this.aBBOXIsVisible){
      let topBarSize = 0
      let modificationRatio = 1
      
      if(this.state.fullscreen){
        const currHeightWidthRatio = window.innerHeight/window.innerWidth
        
        if(currHeightWidthRatio > this.standardHeightWidthRatio ){
          modificationRatio  = window.innerWidth/640
          topBarSize = Math.round(((window.innerHeight-360*modificationRatio))/2)
        }
      }

      if (this.state.aBBOXIsVisible){
        console.log(this.state)
        const top = modificationRatio*this.state.currBBOX[0] + topBarSize
        const right = modificationRatio*this.state.currBBOX[1]
        const bottom = modificationRatio*this.state.currBBOX[2] + topBarSize
        const left = modificationRatio*this.state.currBBOX[3]
        if (!(y >= top && y <= bottom && x >= left && x <= right)){
          this.play()
          this.setState({
            visibleBoundingBox : "",
            aBBOXIsVisible : false,
            currBBOX : null
          })
        }
      } else{
        for (var i =0; i < this.state.currBBoxInfo.length; i++){
          const top = modificationRatio*this.state.currBBoxInfo[i][0] + topBarSize
          const right = modificationRatio*this.state.currBBoxInfo[i][1]
          const bottom = modificationRatio*this.state.currBBoxInfo[i][2] + topBarSize
          const left = modificationRatio*this.state.currBBoxInfo[i][3]
          
          if (y >= top && y <= bottom && x >= left && x <= right){
            this.pause()
            this.setState({
              visibleBoundingBox : <div className = "faceBox" style={{  position : "absolute", top : top, width : right - left, height : bottom - top, left : left}} onMouseLeave={this.mouseExitPlayer}> </div>,
              aBBOXIsVisible : true,
              currBBOX : this.state.currBBoxInfo[i]
            })
            break
          } else {
            this.play()
            this.setState({
              visibleBoundingBox : "",
              aBBOXIsVisible : false,
              currBBOX : null
            })
          }
        }
      }
    }
    

  }

  // SO i might need to have a separate BBOX induced pause thing to handle all teh cases
  // so that I don't unpause when mousing past faces.
  mouseExitPlayer(){
    this.play()
    this.setState({
      visibleBoundingBox : "",
      aBBOXIsVisible : false,
      currBBOX : null
    })
  }

  faceBoundingBoxes(){
    if (this.playerContainerRef === undefined || this.state.progress === 0){
      return []
    }
    const playerRect = this.playerContainerRef.getBoundingClientRect()
    const boxInfo = mapthing[Math.round(this.state.progFractionForFaces * 150289)]
    // bachelor frame count 150289
    // debate fraem count 228398
    
    if (boxInfo === undefined){
      // console.log("HI")
      return []
    } 
    // console.log(boxInfo.length)
    // console.log(Math.round(this.state.progFractionForFaces * 150289))
    // console.log(boxInfo)
    let topBarSize = 0
    let modificationRatio = 1 
    if(this.state.fullscreen){
      const currHeightWidthRatio = window.innerHeight/window.innerWidth
      
      if(currHeightWidthRatio > this.standardHeightWidthRatio ){
        modificationRatio  = window.innerWidth/640
        topBarSize = Math.round(((window.innerHeight-360*modificationRatio))/2)
      }
    }
    let boxList = []
    for (var i =0; i < boxInfo.length; i++){
      const top = modificationRatio*boxInfo[i][0] + topBarSize
      const right = modificationRatio*boxInfo[i][1]
      const bottom = modificationRatio*boxInfo[i][2] + topBarSize
      const left = modificationRatio*boxInfo[i][3]
      
      // boxList.push(<div key = {i} className = "faceBox" style={{  position : "absolute", top : yPos, left : xPos, width : width, height : height}}>

      // </div>)
      // 
      boxList.push(<div key = {i} className = "faceBox" style={{  position : "absolute", top : top, width : right - left, height : bottom - top, left : left}}>

      </div>)
      
    }
    return(
      boxList
    )
  }

  

  pause(){
    clearTimeout(this.timeoutHack)
    this.setState({
      playing : false
    })
    
  }

  play(){
    this.setState({
      playing : true
    })
    this.hackyTimeoutAdder()
    
  }


  pauseUnpause(){
    
    clearTimeout(this.timeoutHack)
    this.setState({
      playing : !this.state.playing
    })
    if (this.state.playing){
      this.hackyTimeoutAdder()
    }
    // React.findDOMNode(this.centerPlayButtonRef).setAttribute('opacity', 1)

    
  }
  getVideoLengthSeconds(){
    return this.videoLengthSeconds
  }

  getProgress(){
    return this.progress
  }

  deliverPlayPauseIcon(){
    return (
    !this.state.playing ?
    <PlayArrowIcon className='playButtonIcon'/> :
    <PauseIcon className='playButtonIcon'/>
    )
  }

  setVolume(val){
    this.setState({
      volume : (val/100)
    })
  }

  toggleFullScreen(){
    screenfull.toggle(this.playerContainerRef)
  }

  muteUnmute(){
    this.setState({
      muted : !this.state.muted
    })
    
  }




  getVolume(){
    if (this.state.muted){
      return 0
    } else {
      return this.state.volume
    }
  }
  deliverVolumeIcon() {
    return (
      !this.state.muted ?
      <VolumeUpIcon fontSize = "small"></VolumeUpIcon> :
      <VolumeMuteIcon fontSize = "small"></VolumeMuteIcon>
    )
  }

  

  deliverPlayPauseIconBottomBar(){
    
    return (
    !this.state.playing ?
    <PlayArrowIcon className='bottomBarPlayButtonIcon'/> :
    <PauseIcon className='bottomBarPlayButtonIcon'/>
    )
  }

  setStateVidDuration(){
    this.setState({
      videoLengthSeconds : this.playerRef.getDuration()
    })
    this.hackyTimeoutIncrement = 0.033/(this.state.videoLengthSeconds)
  }

  setVidTime(e, value){
    this.setStateVidDuration()
    this.playerRef.seekTo(value)
    this.setState({
      progress : value
    })
  }


  ValueLabelComponent(value) {
  
    return (
      <Tooltip enterTouchDelay={0} placement="top" title={value}>
      </Tooltip>
    );
  }

  setVisibleControls(visibility){
    this.setState({
      visibleControls : visibility
    })
  }

  setMouseMove(){
    clearTimeout(this.state.timeout)
    this.setVisibleControls(true)
    this.setState({
      timeout : setTimeout(() => this.setVisibleControls(false), 2000)
    })

  }

  componentDidMount(){
    if (screenfull.isEnabled) {
      screenfull.on('change', () => {
        this.setState({
          fullscreen : !this.state.fullscreen
        });
      });
    }
  }

  render() {
    return (
    <div>
        <AppBar>
          <Toolbar>
            <Typography variant="h6">React Video Player</Typography>
          </Toolbar>
        </AppBar>
        <Toolbar/>
        <div   className='container'>
          <div className='innerContainer' ref={r => {this.playerContainerRef = r}} onMouseEnter={() => this.setVisibleControls(true)} onMouseLeave={() => this.setVisibleControls(false)} onMouseMove={e => this.setMouseMove(e)}>
            <div className="playerWrapper" onMouseMove={this._onMouseMove.bind(this)} onMouseLeave={this.mouseExitPlayer}>
              {this.state.visibleBoundingBox}
              <ReactPlayer
                ref={p => { this.playerRef = p }}
                controls={false}
                muted={false}
                volume={this.getVolume()}
                url="https://vimeo.com/258944633"
                progressInterval={30}
                playing={this.state.playing}
                onStart={this.setStateVidDuration}
                onProgress={this.handleProgress}
                height="100%"
                width={"100%"}
              />
              <div className="playerControlsWrapper">
                {/* <Toolbar>
                  <Typography className='vidTitle'> Video Title</Typography>
                </Toolbar> */}
                <div className='midControlSection' onClick={this.pauseUnpause} onMouseMove={this._onMouseMove.bind(this)}>
                  <div className='midControlSectionContolHolder' style={this.state.visibleControls ? {height: "40%"} : {height: "100%"}}>
                   {/* <button className="buttonStyle playButtonCenter" style={this.state.visibleControls ? {} : {visibility : "hidden"}}> */}
                   {/* ref={p => {this.centerPlayButtonRef = p}} */}
                      {/* {this.deliverPlayPauseIcon()}
                    </button> */}
                  </div>
                </div>
                {this.state.visibleControls ? 
                <BottomControlBar videoLengthSeconds = {this.state.videoLengthSeconds} setVidTime = {this.setVidTime.bind(this)} progress={this.state.progress} pauseUnpause={this.pauseUnpause.bind(this)} muteUnmute={this.muteUnmute.bind(this)} deliverPlayPauseIconBottomBar={this.deliverPlayPauseIconBottomBar.bind(this)} deliverVolumeIcon={this.deliverVolumeIcon.bind(this)} toggleFullScreen={this.toggleFullScreen.bind(this)} setVolume={this.setVolume.bind(this)}></BottomControlBar> 
                : <div/>}

              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default App;


