import NavBar from "./NavBar";
import {useEffect, useState} from "react";
import {useEtherBalance, useEthers} from "@usedapp/core";
import {providers} from "ethers";
import {CircularProgress} from "@mui/material";
import Main from "./Main";
import {getDeployedContract} from "../contractUtils";
import {utils} from "ethers/lib.esm";

function App() {
    const [contract, setContract] = useState(null)
    const [loading, setLoading] = useState(false)
    const [alert, setAlert] = useState(null)

    const {account, activateBrowserWallet, chainId} = useEthers()
    const accountBalance = useEtherBalance(account)
    const contractBalance = useEtherBalance(contract?.address)

    const isConnected = account !== undefined

    useEffect(() => {
        const provider = new providers.Web3Provider(window.ethereum, "any")
        provider.on("network", (newNetwork, oldNetwork) => {
            // When a Provider makes its initial connection, it emits a "network"
            // event with a null oldNetwork along with the newNetwork. So, if the
            // oldNetwork exists, it represents a changing network
            if (oldNetwork) {
                window.location.reload()
            }
        })
    }, [])

    useEffect(() => {
        if (!account || contract)
            return
        const run = async () => {
            setLoading(true)
            const contract = await getDeployedContract()
            if (contract) {
                setContract(contract)
                setLoading(false)
            } else {
                window.alert('Please connect to Rinkeby Test Network')
            }
        }
        run()
    }, [account, chainId])

    const makeBet = async (head, betAmount) => {
        if (betAmount < 0.001 || betAmount > +utils.formatEther(contractBalance))
            return
        try {
            const startTime = new Date()
            setLoading(true)
            const gameId = await contract.callStatic.play(head, {value: utils.parseEther(betAmount)})
            console.log(gameId)
            const filter = contract.filters.Result(gameId)
            contract.once(filter, (gameId, player, amount, won) => {
                console.log(gameId.toNumber(), player, utils.formatEther(amount), won)
                console.log('Time taken:', new Date() - startTime)
                setLoading(false)
                setAlert({
                    className: won ? 'success' : 'danger',
                    result: won ? 'WON' : 'LOST',
                    outcome: won ? (head ? 'HEADS' : 'TAILS') : (head ? 'TAILS' : 'HEADS')
                })
                setTimeout(() => setAlert(null), 2000)
            })
            const tx = await contract.play(head, {value: utils.parseEther(betAmount)})
            await tx.wait(1)
        } catch (e) {
            console.error(e)
        }
    }

    return (
        <div>
            <NavBar account={account}/>
            {
                alert ?
                    <div className={`alert alert-${alert.className} p-2`} role="alert">
                        {`It's a ${alert.outcome}. You ${alert.result} the bet.`}
                    </div> : ""
            }
            {
                loading
                    ? <div style={{height: "80vh", display: "flex", justifyContent: "center", alignItems: "center"}}>
                        <CircularProgress size={80}/>
                    </div>
                    : <div>
                        {
                            isConnected
                                ? <Main
                                    accountBalance={accountBalance}
                                    maxBetAmount={contractBalance}
                                    makeBet={makeBet}
                                />
                                : <div className="text-center mt-4">
                                    <p style={{fontSize: 20}}>Connect to your Metamask wallet</p>
                                    <button className="btn btn-primary" onClick={activateBrowserWallet}>Connect</button>
                                </div>
                        }
                    </div>
            }
        </div>
    );
}

export default App;
