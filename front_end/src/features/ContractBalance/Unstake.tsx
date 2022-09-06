import React, { useState, useEffect } from "react"
import {
  Button,
  CircularProgress,
  Snackbar,
  makeStyles,
} from "@material-ui/core"
import { Token } from "../Main"
import { useUnstakeTokens } from "../../hooks"
import { useContractBalance } from "../../hooks"
import Alert from "@material-ui/lab/Alert"
import { useNotifications } from "@usedapp/core"
import { formatUnits } from "@ethersproject/units"
import { BalanceMsg } from "../../components"

export interface UnstakeFormProps {
  token: Token
}

const useStyles = makeStyles((theme) => ({
  contentContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-start",
    gap: theme.spacing(2),
  },
}))

export const Unstake = ({ token }: UnstakeFormProps) => {
  const { image, address: tokenAddress, name } = token

  const { notifications } = useNotifications()

  const balance = useContractBalance(tokenAddress)

  const formattedBalance: number = balance
    ? parseFloat(formatUnits(balance, 18))
    : 0

  const { send: unstakeTokensSend, state: unstakeTokensState } =
    useUnstakeTokens(tokenAddress)

  const handleUnstakeSubmit = () => {
    return unstakeTokensSend(tokenAddress)
  }

  const [showUnstakeSuccess, setShowUnstakeSuccess] = useState(false)

  const handleCloseSnack = () => {
    showUnstakeSuccess && setShowUnstakeSuccess(false)
  }

  useEffect(() => {
    if (
      notifications.filter(
        (notification) =>
          notification.type === "transactionSucceed" &&
          notification.transactionName === "Unstake tokens"
      ).length > 0
    ) {
      !showUnstakeSuccess && setShowUnstakeSuccess(true)
    }
  }, [notifications, showUnstakeSuccess])

  const isMining = unstakeTokensState.status === "Mining"


  const classes = useStyles()

  return (
    <>
      <div className={classes.contentContainer}>
        <BalanceMsg
          label={`Staked token ${name} balance`}
          amount={formattedBalance}
          tokenImgSrc={image}
        />
      </div>
    </>
  )
}
