import './index.css';
import { useState } from "react";
import { Canvas, useLoader } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";


function Model({ url, color, position, rotation }) {
  const object = useLoader(STLLoader, url);

  return (
    <mesh scale={0.02} position={position} rotation={rotation}>
      <primitive object={object} />
      <meshStandardMaterial color={color} /> 
    </mesh>
  )
}

function ColorOption({ optionTitle, activeColor, setActiveColor, colorOptions }) {
  const colorMappings = {
    "Blue"  : "bg-blue-600",
    "Black" : "bg-black",
    "White" : "bg-white",
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white m-5">
      <div className="p-2">
        <div className="text-center">{optionTitle}</div>
        <div className="flex flex-row justify-center">
          {colorOptions.map((color) => (
            <button 
              className={`rounded-full max-h-0 p-5 m-2 border-2 border-slate-200 
                ${colorMappings[color]}
                ${color === activeColor ? "outline outline-indigo-500 outline-offset-2" : ""}`}
              key={color}
              onClick={() => setActiveColor(color)} />
          ))}
        </div>
      </div>
    </div>
  )
}

function FusesOptions({ fuses, setFuses }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white m-5 flex flex-col">
      <div className="text-center py-4">Amount of Fuses</div>
        <button onClick={() => setFuses(0)} className={`max-h-0 p-5 flex items-center border-t border-slate-200 ${fuses === 0 ? "ring ring-inset ring-indigo-500" : ""}`}>
          0 Fuses
        </button>
        <button onClick={() => setFuses(1)} className={`max-h-0 p-5 flex items-center border-t border-slate-200 ${fuses === 1 ? "ring ring-inset ring-indigo-500" : ""}`}>
          1 Fuse
        </button>
        <button onClick={() => setFuses(2)} className={`rounded-b-lg max-h-0 p-5 flex items-center border-t border-slate-200  ${fuses === 2 ? "ring ring-inset ring-indigo-500" : ""}`}>
          2 Fuses
        </button>
    </div>
  )
}

function App() {
  const topColors = ["Blue", "Black", "White"];
  const bottomColors = ["Blue", "Black", "White"];

  const [topColor, setTopColor] = useState(topColors[0]);
  const [bottomColor, setBottomColor] = useState(bottomColors[0]);
  const [fuses, setFuses] = useState(1);

  function sendOrder(e) {
    e.preventDefault();

    const url = "http://127.0.0.1:8000"; // hardcoded ;-) change if neccessary
    const options = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        top_color: topColor,
        bottom_color: bottomColor, 
        fuses: fuses, 
        pcb_holes: fuses*2
    })};

    fetch(url, options)
      .then(response => response.json())
      .then(response => console.log(response))
  }

  return (
    <div className="relative inline-block h-screen w-screen"> 
      <Canvas>
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
        <pointLight position={[-10, -10, -10]} />
        <OrbitControls />
        <Model url={'./assets/Top.STL'} color={topColor} position={[1.2, -0.1, 0]} rotation={[0, Math.PI, 0]} />
        <Model url={'./assets/Bund.STL'} color={bottomColor} position={[0, 0, 0]} rotation={[Math.PI, 0, 0]} />
        <Model url={'./assets/PCB.STL'} color={"Green"} position={[0.05, 0.07, 0]} rotation={[Math.PI, 0, 0]} />
        {/* <Model url={'./assets/Sikring.STL'} color={"Green"} position={[0.05, 0.07, 0]} rotation={[Math.PI, 0, 0]}/> */}
      </Canvas>
      <div className="rounded-lg z-1 absolute block right-0 top-0 w-96 flex flex-col justify-center w-90 bg-slate-50 border-2 border-slate-200 m-5">
        <div className="p-2">
          <ColorOption optionTitle={"Top Cover"} activeColor={topColor} setActiveColor={setTopColor} colorOptions={topColors}/>
          <ColorOption optionTitle={"Bottom Cover"} activeColor={bottomColor} setActiveColor={setBottomColor} colorOptions={bottomColors}/>
          <FusesOptions fuses={fuses} setFuses={setFuses} />
          <div className="rounded-lg border border-slate-200 bg-indigo-500 m-5">
            <button className="p-5 text-white" onClick={sendOrder}>Send order</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
