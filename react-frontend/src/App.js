import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import axios from 'axios';

class App extends Component {

  constructor(props) {
      super(props);
      this.state ={
        file: null,
        label: null
      }
      this.onFormSubmit = this.onFormSubmit.bind(this)
      this.onChange = this.onChange.bind(this)
      this.fileUpload = this.fileUpload.bind(this)
    }

  onFormSubmit(event) {
    event.preventDefault()
    this.fileUpload(this.state.file)
      .then((resp) => {
        this.setState({
          label: resp.data
        })
      })
  }

  onChange(event) {
    this.setState({
      file: event.target.files[0]
    })
  }

  fileUpload(file){
    const url = 'http://localhost:8000/predict';
    const formData = new FormData();
    formData.append('file',file)
    const config = {
        headers: {'content-type': 'multipart/form-data'}
    }
    return axios.post(url, formData, config)
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Flower Classification Using</h1>
          <h1>Deep Convolutional Neural Networks</h1>
          <h4>Hi! This is a machine that lets you know what</h4>
          <h4>species of flower is in an image!</h4>
          <h4>Try uploading an image of a flower, and press predict!</h4>
          <form onSubmit={this.onFormSubmit}>
            <input type="file" onChange={this.onChange} />
            <button type="submit">Predict</button>
          </form>
          {this.state.label}
        </header>
      </div>
    );
  }
}

export default App;
