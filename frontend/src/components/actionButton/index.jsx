import React from 'react';
import styled from 'styled-components';

const Button = styled.button`
  color:white;
  display: block;
  width: ${props => props.isBigger ? 320 : 280}px;
  height: ${props => props.isBigger ? 80 : 60}px;
  line-height: ${props => props.isBigger ? '83px' : '60px'};
  background-color: transparent;
  border: 3px solid #0085FF;
  border-radius: 8px;
  box-shadow: 0px 4px 4px #000000;
  transition: .1s all ease-out;
  &:active{
    border-color: #303030;
    background-color: #0085FF;
  }
`;

export default function ActionButton(props) {
  return (
    <Button
      isBigger={props.isBigger}
      onClick={props.onClick}
    >
      {props.children}
    </Button>
  )
}