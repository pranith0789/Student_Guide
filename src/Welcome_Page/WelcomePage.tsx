// src/components/WelcomePage.tsx
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Text } from '@react-three/drei';
import { useNavigate } from 'react-router-dom';
import { useRef } from 'react';
import * as THREE from 'three';

const FloatingText = () => {
  const textRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (textRef.current) {
      textRef.current.position.y = Math.sin(clock.getElapsedTime()) * 0.2;
      textRef.current.rotation.y += 0.005;
    }
  });

  return (
    <Text
      ref={textRef}
      fontSize={1}
      color="hotpink"
      anchorX="center"
      anchorY="middle"
    >
      Welcome
    </Text>
  );
};

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="relative w-screen h-screen overflow-hidden">
      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 3, 4]} intensity={1} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade />
        <OrbitControls enableZoom={false} />
        <FloatingText />
      </Canvas>

      {/* UI Overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-black bg-opacity-40 text-white text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-4 drop-shadow-lg">Expand your knowledge base</h1>
        <p className="text-lg md:text-xl mb-6 max-w-md">Begin your journey with an amazing AI Tutor</p>
        <div className="space-x-4">
          <button
            onClick={() => navigate('/Login')}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition text-white font-semibold"
          >
            Login
          </button>
          <button
            onClick={() => navigate('/Signup')}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-md transition text-white font-semibold"
          >
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;
