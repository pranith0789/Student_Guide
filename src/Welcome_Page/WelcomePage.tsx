// src/components/WelcomePage.tsx
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Text } from '@react-three/drei';
import { useNavigate } from 'react-router-dom';
import { useRef } from 'react';
import * as THREE from 'three';

// Floating and rotating welcome text
const FloatingText = () => {
  const textRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const time = clock.getElapsedTime();
    if (textRef.current) {
      textRef.current.position.y = Math.sin(time) * 0.2;
      textRef.current.rotation.y += 0.005;
      const scale = 1 + 0.05 * Math.sin(time * 2);
      textRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <Text
      ref={textRef}
      fontSize={1}
      color="hotpink"
      anchorX="center"
      anchorY="middle"
      outlineWidth={0.03}
      outlineColor="white"
      outlineOpacity={0.8}
      strokeColor="white"
      strokeWidth={0.015}
    >
      Welcome
    </Text>
  );
};

// Rotating cube component
const RotatingCube = ({ position }: { position: [number, number, number] }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.01;
      meshRef.current.rotation.y += 0.01;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[0.5, 0.5, 0.5]} />
      <meshStandardMaterial color="#00ffff" wireframe />
    </mesh>
  );
};

// Floating sphere component
const FloatingSphere = ({ position }: { position: [number, number, number] }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.position.y = position[1] + Math.sin(clock.getElapsedTime() + position[0]) * 0.3;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.3, 32, 32]} />
      <meshStandardMaterial color="violet" transparent opacity={0.7} />
    </mesh>
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

        {/* Centered animated text */}
        <FloatingText />

        {/* Background animated 3D objects */}
        <RotatingCube position={[-2, 1, -2]} />
        <RotatingCube position={[2, -1, -3]} />
        <FloatingSphere position={[1.5, 1.5, -2]} />
        <FloatingSphere position={[-1.5, -1.2, -1.5]} />
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
