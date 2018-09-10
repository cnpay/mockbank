### b2c-bank 模拟上游支付通道，功能列表
1. b2c支付
2. b2c查询
3. 代付接口 [增加一笔商户扣款交易]
4. 余额查询
5. 交易查询
6. 快捷支付[就是api支付]
7. 后台交易通知 [定时任务]

### 技术log
1. sqlite3不支持中划线表名
2. 自动化网页前端测试 https://github.com/cobrateam/splinter https://splinter.readthedocs.io/en/latest/
3. bigpay的渠道路由、分流规则改造，可以考虑升级到jdk8后采用规则引挚 https://github.com/j-easy/easy-rules or https://github.com/rulebook-rules/rulebook
4. 最好的管理后台生成技术，还是vue组件机制 https://github.com/almasaeed2010/AdminLTE https://github.com/PanJiaChen/vue-element-admin/

### 商业思路 -- 支付全方位服务
1. 像贝密一样开源三/四方方支付系统，提供技术支持，开源并让自己的小兄弟加入，采用spring-cloud体系
2. 维护一个awesome-pay和支付相关的深度网站(大家参与)，上知乎,github上推广自己的知识和分享
3. 做一个专业支付服务和支持的团队: 有一个专业维护的网站(技术[代运维]、法规[代设计]、跨境、商机[费率比较]、中介)
4. 已经有竞争对手 
    1. https://github.com/jmdhappy/xxpay-master
    2. https://github.com/jigsaw-projects/jigsaw-payment
    3. https://github.com/helei112g/payment
5. 自已实现的系统进行差异化竞争： 重点支持二清(叫集团)商户模式

### 人生感悟
1. 先付出再求回报
2. 把自己专业的东西包装输出就是创业
3. 不要脱离产业
4. 找到自己的价值和定位