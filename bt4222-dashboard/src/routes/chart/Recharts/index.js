import React from 'react'
import { Radio, Select } from 'antd'
import { Page } from 'components'
import ReChartsComponent from './ReChartsComponent'
import styles from './index.less'

const RadioGroup = Radio.Group

const chartList = [
  {
    label: 'lineChart',
    value: 'lineChart',
  },
  {
    label: 'barChart',
    value: 'barChart',
  },
  {
    label: 'areaChart',
    value: 'areaChart',
  },
]

class Chart extends React.Component {
  constructor () {
    super()
    this.state = {
      type: 'androidcentral-Acer',
    }
    this.handleChange = this.handleChange.bind(this)
  }
  handleChange (e) {
    this.setState({
      type: e
    })
  }
  render () {
    return (<Page inner>
      <Select defaultValue="androidcentral-ASUS" style={{ width: 120 }} onChange={this.handleChange}>
      <Option value="androidcentral-Acer">Acer</Option>
        <Option value="androidcentral-ASUS">ASUS</Option>
        <Option value="androidcentral-Blu">Blu</Option>
      </Select>
      <div className={styles.chart}>
        <ReChartsComponent type={this.state.type} />
      </div>
    </Page>)
  }
}


export default Chart
