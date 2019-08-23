import { mount } from '@vue/test-utils'
import HelloWorld from '@/components/HelloWorld'

// describe('HelloWorld.vue', () => {
test('renders props.msg when passed', () => {
  // const msg = 'new message'
  const wrapper = mount(HelloWorld, {
    propsData: {
      value: 'new message'
    }
  })
  expect(wrapper).toMatchSnapshot()
})
// })
