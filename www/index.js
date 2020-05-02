const dateFormat = 'DD.MM.YYYY',
      dayWidth = 25,
      eventHeight = 65,
      monthNames = [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
    ]
;

function renderTripper(weekendList, eventSource, tagGroups){
    // Calendar first month
    const today = moment().startOf('day'),
          eventList = getEvents(eventSource)
    ;

    const app = new Vue({
        el: '#app',
        data: {
            width: 0,
            height: 0,
            tags: tagGroups,
            applyTags: [],
            applySearch: '',
            months: [],
            stripes: [],
            detail: {
                show: false,
                event: null,
            },
        },
        filters: {
            pluralize: function(value, one, two, three){
                const cases = [2, 0, 1, 1, 1, 2],
                     titles = [one, two, three],
                        key = (value % 100 > 4 && value % 100 < 20) ? 2 : cases[(value % 10 < 5) ? value % 10 : 5]
                ;
                return titles[key];
            }
        },
        created: function() {
            const self = this,
                  urlParams = new URLSearchParams(window.location.search),
                  tags = parseInt(urlParams.get('tags')),
                  search = urlParams.get('q');

            if (tags){
                this.tags.map(function(g){
                    g.tags.map(function(t){
                        if (t.bit & tags) {
                            self.applyTags.push(t.bit);
                        }
                    });
                });
            }

            if (search){
                this.applySearch = search.trim();
            }
        },
        computed: {
            eventFilter(){
                let self = this,
                    events = eventList,
                    params = {
                        q: this.applySearch.trim().toLowerCase(),
                        tags: 0,
                    }
                ;

                params.tags = this.applyTags.reduce((r, b) => r |= b, params.tags);
                let newUrl = window.location.href.split('?')[0],
                    newParams = Object.entries(params)
                        .filter(([k, v]) => v)
                        .map((i) => i.join('='))
                        .join('&')
                ;

                window.history.replaceState(
                    {},
                    null,
                    newParams ? newUrl += '?' + newParams: newUrl
                );

                if (params.q){
                    events = events.filter((e) => e.norm.indexOf(params.q) != -1);
                }

                this.tags.forEach(function(g){
                    // Collects possible events
                    let groupEvents = events;
                    self.tags.forEach(function(j){
                        let bits = params.tags & j.bits;
                        if (bits && j.bits != g.bits) {
                            groupEvents = groupEvents.filter((e) => bits & e.tags)
                        }
                    });

                    // Marks active tags
                    let eventsMask = 0;
                    groupEvents.forEach((e) => eventsMask |= e.tags);
                    g.tags.forEach((t) => t.active = eventsMask & t.bit);

                    // Filters gant events
                    let applyBits = params.tags & g.bits;
                    if (applyBits) {
                        events = events.filter((e) => applyBits & e.tags);
                    }
                });

                if (!events.length) {
                    return events;
                }

                events = masonry(events);

                let firstDate = events[0].start.clone();
                let lastDate = events.reduce((r, e) => r < e.end ? e.end : r, firstDate);

                this.months = getMonths(today, firstDate, lastDate, weekendList);
                this.width = this.months.reduce((r, m) => r + m.days.length, 0) * dayWidth;
                this.height = events.reduce((r, e) => Math.max(r, e.voffset), 0) + eventHeight * 2;

                // Renders background weekend stripes
                let strip_i = 0;
                this.stripes = []
                this.months.map(function(month){
                    month.days.map(function(day){
                        if (strip_i && self.stripes[strip_i - 1].is_weekend === day.is_weekend){
                            self.stripes[strip_i - 1].width += dayWidth;
                        } else {
                            self.stripes.push({
                                is_weekend: day.is_weekend,
                                width: dayWidth,
                            })
                            strip_i++;
                        }
                    });
                });
                return events;
            }
        },
        methods: {
            showDetail: function(event){
                this.detail.event = event;
            },
            hideDetail: function(){
                this.detail.event = null;
            }
        }
    });
}

function getEvents(eventSource, tagGroups) {
    let eventList = [];

    for (let i = 0; i < eventSource.length; i++){
        let source = eventSource[i];
        start = moment(source.start, dateFormat);
        end = moment(source.end, dateFormat);
        const days = end.diff(start, 'days') + 1;
        event = Object.assign(source, {
               id: 'gant__event--' + i,
            index: i,
            start: start,
              end: end,
            level: source.level,
             days: days,
          hoffset: 0,
          voffset: 0,
            width: days * dayWidth,
        });

        eventList.push(event);
    }

    // Must sort events
    // Smallest left, biggest right
    return eventList.sort(function(a,b) {
        if (a.start > b.start) {
            return 1;
        } else if (a.start.isSame(b.start)) {
            // Puts longest first
            return b.end - a.end;
        }
        return -1;
    });
}

function getMonths(today, firstDate, lastDate, weekendList){
    let monthList = [];

    // Creates months rule
    const monthLen = lastDate.clone().startOf('month').diff(firstDate.clone().startOf('month'), 'months');
    for (let i = 0; i <= monthLen; i++) {
        let month = moment(firstDate),
            days = [];
        month.add(i, 'month');

        let total = month.daysInMonth();
        for (let y = 0; y < total; y++){
            let d = moment(month);
            d.date(y + 1)

            if (d < firstDate || d > lastDate) {
                continue
            }

            days.push({
                date: d,
                is_weekend: d.isoWeekday() >= 6 || weekendList.indexOf(d.format(dateFormat)) > -1,
                is_today: d.format(dateFormat) == today.format(dateFormat),
            });
        }

        let name = monthNames[month.month()];
        if (month.month() == 0 && month.year() > today.year()) {
            name = name + ' ' + month.year()
        }

        monthList.push({
            name: name,
            days: days,
        });
    }

    return monthList;
}

function masonry(eventList){
    let events = [],
        seen = [],
        startDate = eventList[0].start
    ;

    for (let i = 0; i < eventList.length; i++) {
        let event = eventList[i];
        event.hoffset = event.start.diff(startDate, 'days') * dayWidth;

        // Moves event down
        // if row place is already taken.
        let found = false;
        for (let y = 0; y < seen.length; y++) {
            let other = seen[y];

            if (other.end < event.start) {
                seen[y] = event;
                event.voffset = y * eventHeight;
                found = true;
                break;
            }
        }

        // If row is empty
        // sets event's end as right border
        if (!found){
            event.voffset = seen.length * eventHeight;
            seen.push(event);
        }
        events.push(event)
    }
    return events
}

// Init
renderTripper(DATA.weekendList, DATA.eventSource, DATA.tagGroups);

// Displays gant and hides loader
document.body.classList.add('active');
setTimeout(function(){
    let blocker = document.getElementById('blocker');
    blocker.parentNode.removeChild(blocker);
}, 400);
