import './index.css';
import { useState, useRef, useEffect } from "react";
import { Canvas, useLoader, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";


function Model({ url, color, position, rotation }) {
  const ref = useRef();
  const object = useLoader(STLLoader, url);
  
  return (
    <mesh scale={0.02} position={position} rotation={rotation} ref={ref}>
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
                ${color === activeColor && "outline outline-indigo-500 outline-offset-2"}`}
              key={color}
              onClick={() => setActiveColor(color)} />
          ))}
        </div>
      </div>
    </div>
  )
}

function AdditionalOptions({ optionTitle, optionNames, top, setTop, bottom, setBottom }) {
  const buttonConfig = "rounded-lg w-36 h-0 m-2 mb-5 p-4 flex justify-center items-center border border-slate-200"
  const activeConfig = "ring ring-inset ring-indigo-500"
  return (
    <div className="rounded-lg border border-slate-200 bg-white m-5 flex flex-col">
      <div className="text-center py-4">{optionTitle}s</div>
      <div className="flex flex-row justify-center">
        <button onClick={() => setTop(!top)} className={`${buttonConfig} ${top && activeConfig}`}>
          Top {optionNames}
        </button>
        <button onClick={() => setBottom(!bottom)} className={`${buttonConfig} ${bottom && activeConfig}`}>
          Bottom {optionNames}
        </button>
        </div>
    </div>
  )
}

function App() {
  const topColors = ["Blue", "Black", "White"];
  const bottomColors = ["Blue", "Black", "White"];
  
  const [preview, setPreview] = useState(false);
  const [topColor, setTopColor] = useState(topColors[0]);
  const [bottomColor, setBottomColor] = useState(bottomColors[0]);
  const [topFuse, setTopFuse] = useState(true);
  const [bottomFuse, setBottomFuse] = useState(false);
  const [topHole, setTopHole] = useState(true);
  const [bottomHole, setBottomHole] = useState(true);

  function sendOrder(e) {
    e.preventDefault();

    const url = "http://127.0.0.1:8000"; // hardcoded ;-) change if neccessary
    const options = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        top_color: topColor,
        bottom_color: bottomColor, 
        top_fuse: topFuse,
        bottom_fuse: bottomFuse,
        top_hole: topHole,
        bottom_hole: bottomHole
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
        {preview && <Model url={'./assets/Top.STL'} color={topColor} position={[1.2-0.5, -0.1, 1]} rotation={[0, Math.PI, 0]} />}
        <Model url={'./assets/Bund.STL'} color={bottomColor} position={[0-0.5, 0, 1]} rotation={[Math.PI, 0, 0]} />
        <Model url={'./assets/PCB.STL'} color={"Green"} position={[0.05-0.5, 0.07, 0.92]} rotation={[Math.PI, 0, 0]} />
        {topFuse && <Model url={'./assets/Sikring.STL'} color={"Red"} position={[0.3, -0.05, 0.585]} rotation={[0, 0, Math.PI/2]} />}
        {bottomFuse && <Model url={'./assets/Sikring.STL'} color={"Red"} position={[0.3, -0.05, 0.325]} rotation={[0, 0, Math.PI/2]} />}
      </Canvas>
      <div className="rounded-lg z-1 absolute block right-0 top-0 w-96 flex flex-col justify-center w-90 bg-slate-50 border-2 border-slate-200 m-5">
        <div className="p-2">
          <button className={`w-[89%] h-0 rounded-lg flex justify-center items-center border border-slate-200 bg-white m-5 p-5 ${preview && "ring ring-inset ring-indigo-500"}`} onClick={() => setPreview(!preview)}>Toggle Preview</button>
          <ColorOption optionTitle={"Top Cover"} activeColor={topColor} setActiveColor={setTopColor} colorOptions={topColors}/>
          <ColorOption optionTitle={"Bottom Cover"} activeColor={bottomColor} setActiveColor={setBottomColor} colorOptions={bottomColors}/>
          <AdditionalOptions optionTitle={"Fuses"} optionNames={"Fuse"} top={topFuse} setTop={setTopFuse} bottom={bottomFuse} setBottom={setBottomFuse} />
          <AdditionalOptions optionTitle={"Holes"} optionNames={"Holes"} top={topHole} setTop={setTopHole} bottom={bottomHole} setBottom={setBottomHole} />
          <button className="w-[89%] rounded-lg border border-slate-200 bg-indigo-500 m-5 mt-0 p-5 text-white" onClick={sendOrder}>Send Order</button>
        </div>
      </div>
    </div>
  )
}

export default App
