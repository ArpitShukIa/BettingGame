import React, {useState} from 'react';
import coinToss from "../coin-toss.gif"
import {utils} from "ethers";

function Main({accountBalance, maxBetAmount, makeBet}) {
    const [betAmount, setBetAmount] = useState('')

    return (
        <div style={{height: "85vh", display: "flex", alignItems: "center"}}>
            <div className="card" style={{width: "40%", marginLeft: "30%"}}>
                <img src={coinToss} className="card-img-top w-50 mt-4" alt="#" style={{marginLeft: "25%"}}/>
                <div className="card-body">
                    <h5 className="text-center">Make a bet</h5>
                    <input className="form-control"
                           type="number"
                           step="any"
                           placeholder="Enter bet amount..."
                           value={betAmount}
                           onChange={e => setBetAmount(e.target.value)}
                           required
                    />
                    <div className="mt-3 d-flex justify-content-center">
                        <button
                            className="btn btn-primary w-25"
                            onClick={() => makeBet(true, betAmount)}
                        >
                            Heads
                        </button>
                        <button
                            className="btn btn-danger ms-3 w-25"
                            onClick={() => makeBet(false, betAmount)}
                        >
                            Tails
                        </button>
                    </div>
                    <div className="mt-3">
                        {
                            maxBetAmount ?
                                <span>
                                    <b>Max Bet:</b> {(+utils.formatEther(maxBetAmount)).toFixed(5)} ETH
                                </span> : ""
                        }
                        {
                            accountBalance ?
                                <span className="float-end">
                                    <b>Balance:</b> {(+utils.formatEther(accountBalance)).toFixed(5)} ETH
                                </span> : ""
                        }
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Main;