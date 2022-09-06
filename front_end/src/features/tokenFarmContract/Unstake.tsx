import React, { useState, useEffect } from "react"
import {
  Button,
  CircularProgress,
  Snackbar,
  makeStyles,
} from "@material-ui/core"
import { Token } from "../Main"
import { useUnstakeTokens, useStakingBalance } from "../../hooks"
import Alert from "@material-ui/lab/Alert"
import { useNotifications } from "@usedapp/core"
import { formatUnits } from "@ethersproject/units"
import { BalanceMsg } from "../../components"
import { SliderInput } from "../../components"

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
  slider: {
    width: "100%",
    maxWidth: "400px",
  },
}))

export const Unstake = ({ token }: UnstakeFormProps) => {
  const { image, address: tokenAddress, name } = token

  const { notifications } = useNotifications()

  const balance = useStakingBalance(tokenAddress)

  const formattedBalance: number = balance
    ? parseFloat(formatUnits(balance, 18))
    : 0
  const [amount, setAmount] =
    useState<number | string | Array<number | string>>(0)

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
          label={`Balance of ${name} in contract`}
          amount={formattedBalance}
          tokenImgSrc={image}
        />
        <SliderInput
          label={`Loan ${name}`}
          maxValue={formattedBalance}
          id={`slider-input-${name}`}
          className={classes.slider}
          value={amount}
          onChange={setAmount}
          disabled={isMining}
        />
        <Button
          color="primary"
          variant="contained"
          size="large"
          onClick={handleUnstakeSubmit}
          disabled={isMining}
        >
          {isMining ? <CircularProgress size={26} /> : `Take Loan ${name}`}
        </Button>
      </div>
      <Snackbar
        open={showUnstakeSuccess}
        autoHideDuration={5000}
        onClose={handleCloseSnack}
      >
        <Alert onClose={handleCloseSnack} severity="success">
          Took Loan successfully!
        </Alert>
      </Snackbar>
    </>
  )
}
