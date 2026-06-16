<script setup>
import { computed, onMounted, reactive } from 'vue'
import MemberSelect from '../components/MemberSelect.vue'
import StatusBanner from '../components/StatusBanner.vue'
import { useLoyaltyData } from '../stores/useLoyaltyData'

const { state, refreshAll, createOrder, refundOrder } = useLoyaltyData()
const form = reactive({ member_id: '', original_amount: 50, rule_id: '', note: '' })

const selectedMember = computed(() => {
  if (!form.member_id) return null
  return state.members.find(m => m.id === Number(form.member_id))
})

const preview = computed(() => {
  if (!selectedMember.value) return null
  const member = selectedMember.value
  const rule = state.rules.find(r => r.id === Number(form.rule_id))
  if (!rule) return null

  const discountPercent = member.discount_percent
  const discountAmount = Math.round(form.original_amount * discountPercent / 100 * 100) / 100
  const finalAmount = Math.round((form.original_amount - discountAmount) * 100) / 100
  const pointsEarned = Math.floor(finalAmount / rule.amount_per_point * rule.multiplier)

  return {
    discountPercent,
    discountAmount,
    finalAmount,
    pointsEarned
  }
})

onMounted(async () => {
  await refreshAll()
  if (state.members[0]) form.member_id = state.members[0].id
  if (state.rules[0]) form.rule_id = state.rules[0].id
})

async function submitOrder() {
  await createOrder({
    member_id: Number(form.member_id),
    original_amount: Number(form.original_amount),
    rule_id: Number(form.rule_id),
    note: form.note || null
  })
  form.note = ''
}

async function handleRefund(order) {
  if (!confirm(`确定要退款订单 ${order.order_no} 吗？将扣回 ${order.points_earned} 积分。`)) return
  await refundOrder(order.id, { note: '' })
}

function formatStatus(status) {
  const map = {
    completed: '已完成',
    refunded: '已退款'
  }
  return map[status] || status
}
</script>

<template>
  <section class="view-stack">
    <div class="section-header">
      <div>
        <p class="eyebrow">Orders</p>
        <h2>消费订单</h2>
      </div>
      <StatusBanner :error="state.error" :notice="state.notice" :loading="state.loading" />
    </div>

    <div class="two-column">
      <form class="panel" @submit.prevent="submitOrder">
        <h3>录入消费</h3>
        <label>
          会员
          <MemberSelect v-model="form.member_id" :members="state.members" />
        </label>
        <label>
          消费金额（元）
          <input v-model.number="form.original_amount" min="0.01" step="0.01" type="number" />
        </label>
        <label>
          积分规则
          <select v-model.number="form.rule_id">
            <option v-for="rule in state.rules" :key="rule.id" :value="rule.id">
              {{ rule.name }} · x{{ rule.multiplier }}
            </option>
          </select>
        </label>
        <label>
          备注
          <input v-model="form.note" type="text" placeholder="选填" />
        </label>

        <div v-if="preview" class="order-preview">
          <div class="preview-row">
            <span>会员等级折扣</span>
            <strong>{{ preview.discountPercent }}%</strong>
          </div>
          <div class="preview-row">
            <span>优惠金额</span>
            <strong class="discount">-¥{{ preview.discountAmount.toFixed(2) }}</strong>
          </div>
          <div class="preview-row total">
            <span>实付金额</span>
            <strong>¥{{ preview.finalAmount.toFixed(2) }}</strong>
          </div>
          <div class="preview-row">
            <span>获得积分</span>
            <strong class="points">+{{ preview.pointsEarned }}</strong>
          </div>
        </div>

        <button class="primary-button" type="submit">确认下单</button>
      </form>

      <section class="panel wide-panel">
        <h3>订单列表</h3>
        <div class="order-table">
          <div class="order-head">
            <span>订单号</span>
            <span>会员</span>
            <span>原价</span>
            <span>实付</span>
            <span>积分</span>
            <span>状态</span>
            <span>操作</span>
          </div>
          <div v-for="order in state.orders" :key="order.id" class="order-row">
            <span class="order-no">{{ order.order_no }}</span>
            <span>{{ order.member_name }}</span>
            <span class="original">¥{{ order.original_amount.toFixed(2) }}</span>
            <span class="final">¥{{ order.final_amount.toFixed(2) }}</span>
            <span class="points-earned">+{{ order.points_earned }}</span>
            <span>
              <span :class="['status-badge', order.status]">{{ formatStatus(order.status) }}</span>
            </span>
            <span>
              <button
                v-if="order.status === 'completed'"
                class="text-button danger"
                @click="handleRefund(order)"
              >
                退款
              </button>
              <span v-else class="muted">-</span>
            </span>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>
