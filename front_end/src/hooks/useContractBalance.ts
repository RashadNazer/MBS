import { useContractCall, useEthers, useEtherBalance } from "@usedapp/core"
import TokenFarm from "../chain-info/TokenFarm.json"
import { utils, BigNumber, constants } from "ethers"
import networkMapping from "../chain-info/map.json"
import Web3 from 'web3';
/**
 * Get the staking balance of a certain token by the user in our TokenFarm contract
 * @param address - The contract address of the token
 */
export const useContractBalance = (address: string): BigNumber | undefined => {
    const { account, chainId } = useEthers()

    const { abi } = TokenFarm
    const tokenFarmContractAddress = chainId ? networkMapping[String(chainId)]["TokenFarm"][0] : constants.AddressZero

    const tokenFarmInterface = new utils.Interface(abi)

    const [stakingBalance] =
        useContractCall({
            abi: tokenFarmInterface,
            address: tokenFarmContractAddress,
            method: "stakingBalance",
            args: [address],
        }) ?? []

    return stakingBalance
}


