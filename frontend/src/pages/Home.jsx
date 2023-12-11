import React from "react";
import Hero from "../components/Hero.jsx";

const Home = () => {
  return (
    <div className="overflow-hidden bg-black text-white flex justify-center">
      <div className="w-full xl:max-w-[1440px]">
        <Hero />
      </div>
    </div>
  );
};

export default Home;
