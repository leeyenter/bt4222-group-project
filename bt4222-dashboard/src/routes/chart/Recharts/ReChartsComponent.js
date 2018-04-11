import React from 'react'
import PropTypes from 'prop-types'

import AreaChartComponent from './AreaChartComponent'
import BarChartComponent from './BarChartComponent'
import LineChartComponent from './LineChartComponent'


const ReChartsComponent = ({ type }) => {
  let phoneData = require(`../../../results/compiled/${type}.json`);
  let keys = Object.keys(phoneData.interest["Acer Android Phones"]["num_posts"]);
  let dataSource = keys.map((key) => {
    return {
      date: key,
      val: phoneData.interest["Acer Android Phones"]["num_posts"][key]
    }
  });
  return (<LineChartComponent dataSource={dataSource} />)
}

ReChartsComponent.propTypes = {
  type: PropTypes.string,
}

export default ReChartsComponent
