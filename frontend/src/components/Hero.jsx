import React, { useState, useEffect } from "react";
import { blockchainConstants } from "../constants";
import axios from "axios";
import SpinningCircleGray from "../assets/SpinningCircleGray";

const Hero = () => {
  const [selectedChain, setSelectedChain] = useState("BNB");
  const [seconds, setSeconds] = useState(8);
  const [gasFees, setGasFees] = useState({});

  useEffect(() => {
    const getGas = async () => {
      console.log("getGas API run once");
      // axios
      //   .get(`www.gasolina.com/api/v1/gas/${selectedChain}`)
      //   .then((res) => setGasFees(res.data.gas))
      //   .catch((e) => console.log(e));
      setGasFees({
        BNB: {
          Slow: { amount: 0.8, base: 2, dollar: 4, time: 5 },
          Average: { amount: 0.9, base: 2, dollar: 4, time: 5 },
          Fast: { amount: 1.0, base: 2, dollar: 4, time: 5 },
          "Real Time": { amount: 1.0, base: 2, dollar: 4, time: 5 },
        },
        AVAX: {
          Slow: { amount: 0.8, base: 2, dollar: 4, time: 5 },
          Average: { amount: 0.9, base: 2, dollar: 4, time: 5 },
          Fast: { amount: 1.0, base: 2, dollar: 4, time: 5 },
          "Real Time": { amount: 1.0, base: 2, dollar: 4, time: 5 },
        },
        SUI: {
          Slow: { amount: 0.8, base: 2, dollar: 4, time: 5 },
          Average: { amount: 0.9, base: 2, dollar: 4, time: 5 },
          Fast: { amount: 1.0, base: 2, dollar: 4, time: 5 },
          "Real Time": { amount: 1.0, base: 2, dollar: 4, time: 5 },
        },
        MINA: {
          Slow: { amount: 0.8, base: 2, dollar: 4, time: 5 },
          Average: { amount: 0.9, base: 2, dollar: 4, time: 5 },
          Fast: { amount: 1.0, base: 2, dollar: 4, time: 5 },
          "Real Time": { amount: 1.0, base: 2, dollar: 4, time: 5 },
        },
      });
    };
    getGas();

    const id = setInterval(
      () =>
        setSeconds((oldSeconds) => {
          if (oldSeconds === 1) {
            getGas();
            return 8;
          } else {
            return oldSeconds - 1;
          }
        }),
      1000
    );
    return () => {
      clearInterval(id);
    };
  }, []);

  return (
    <div className="mx-24 flex flex-col items-center">
      {/*--title---*/}
      <div className="w-full my-6 flex items-center">
        <div className="bg-white w-[28px] h-[28px] rounded-full"></div>
        <div className="ml-2 text-4xl font-medium">Gasolina</div>
      </div>
      {/*--description---*/}
      <div className="w-[690px] text-center text-5xl leading-[60px] font-medium">Your ultimate destination for multichain gas price prediction</div>
      {/*--network---*/}
      <div>
        <div className="mt-8 w-full text-xl text-center font-medium">Select Network</div>
        <div className="mt-2 flex space-x-3">
          {Object.keys(blockchainConstants).map((chain) => (
            <div
              key={chain}
              className={`${
                selectedChain === chain ? "bg-gray-600" : ""
              } w-[96px] flex flex-col py-2 border-2 border-white rounded-lg hover:bg-gray-600 cursor-pointer`}
              onClick={() => setSelectedChain(chain)}
            >
              <img src={blockchainConstants[chain].img} className="mx-auto w-[50px]" />
              <div className="mt-1 text-3xl text-center">{chain}</div>
            </div>
          ))}
        </div>
      </div>
      {/*--gas---*/}
      <div>
        <div className="mt-10 w-full text-base">Next update in {seconds}s...</div>
        <div className="mt-1 flex space-x-3">
          {["Slow", "Average", "Fast", "Real Time"].map((speed) => (
            <div key={speed} className="w-[154px] h-[170px] flex flex-col justify-between py-3 bg-gray-700 rounded-lg">
              <div className="text-lg text-center">{speed}</div>
              {Object.keys(gasFees).length === 0 ? (
                <div className="grow flex items-center justify-center text-center">
                  <SpinningCircleGray />
                </div>
              ) : (
                <div className="grow flex flex-col">
                  <div className="mt-2 text-center text-xl font-medium">
                    {gasFees[selectedChain][speed].amount} {blockchainConstants[selectedChain].unit}
                  </div>
                  <div className="mt-3 text-center text-sm font-medium">
                    Base: {gasFees[selectedChain][speed].amount} {blockchainConstants[selectedChain].unit}
                  </div>
                  <div className="text-center text-sm font-medium">${gasFees[selectedChain][speed].dollar}</div>
                  <div className="text-center text-sm font-medium">
                    {Math.floor(gasFees[selectedChain][speed].time / 60)} min {gasFees[selectedChain][speed].time % 60} seconds
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      {/*--historical price---*/}
      <div className="mt-16 text-3xl font-medium">Gas Price History</div>
      <div className="mt-4">graph</div>
      {/*--browser extension---*/}
      <div className="mt-12 text-3xl font-medium">Download Browser Extension</div>
      <div className="mt-8 flex space-x-8">
        {["Chrome", "Firefox"].map((browser) => (
          <div className="flex flex-col items-center w-[200px] py-6 border-[3px] border-white rounded-xl">
            <div className="w-[50px] h-[50px] rounded-full bg-gray-300"></div>
            <div className="mt-2">{browser}</div>
            <div className="mt-4 px-3 py-2 text-xs border border-white text-center rounded-md hover:bg-gray-400 cursor-pointer">
              DOWNLOAD EXTENSION
            </div>
          </div>
        ))}
      </div>
      {/*--heat map---*/}
      <div className="mt-16 text-3xl font-medium">Gas Price Heatmap</div>
      <div className="mt-4">graph</div>
      {/*--API integration---*/}
      <div className="mt-16 text-3xl font-medium">Get API Integration</div>
      <div className="mt-8 w-[78%] flex">
        <div className="w-[50%]">
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec accumsan ut tortor ac mattis. Nulla mattis mollis fringilla. Donec sed
            turpis ac metus vehicula bibendum.
          </p>
          <p className="mt-3">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec accumsan ut tortor ac mattis. Nulla mattis mollis fringilla. Donec sed
            turpis ac metus vehicula bibendum.
          </p>
        </div>
        <div className="w-[50%]"></div>
      </div>
      {/*--footer---*/}
      <div className="w-[78%] mt-16 mb-16 text-base">
        <div className="flex space-x-4">
          {["About", "Gas Price", "API", "Web Extension", "Subscription", "FAQ", "Contact Us"].map((text) => (
            <div className="hover:underline cursor-pointer">{text}</div>
          ))}
        </div>
        <div className="w-full flex justify-end items-center">
          <div className="bg-white w-[28px] h-[28px] rounded-full"></div>
          <div className="ml-2 text-4xl font-medium">Gasolina</div>
        </div>
        <div className="w-full flex justify-end">Gasolina 2023 All Rights Reserved</div>
      </div>
    </div>
  );
};

export default Hero;
