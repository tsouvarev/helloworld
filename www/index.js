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
          eventList = getEvents(today, eventSource)
    ;

    const app = new Vue({
        el: '#app',
        data: {
            width: 0,
            height: 0,
            bgUrl: '',
            tags: tagGroups,
            applyTags: [],
            applySearch: '',
            months: [],
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
        computed: {
            eventFilter(){
                let self = this,
                    events = eventList
                ;

                if (this.applySearch){
                    let find = this.applySearch.toLowerCase();
                    events = events.filter((e) => e.search.indexOf(find) != -1);
                }

                let applyTags = 0;
                this.applyTags.forEach((b) => applyTags |= b);
                this.tags.forEach(function(g){
                    // Collects possible events
                    let groupEvents = events;
                    self.tags.forEach(function(j){
                        let bits = applyTags & j.bits;
                        if (bits && j.bits != g.bits) {
                            groupEvents = groupEvents.filter((e) => bits & e.tags)
                        }
                    });

                    // Marks active tags
                    let eventsMask = 0;
                    groupEvents.forEach((e) => eventsMask |= e.tags);
                    g.tags.forEach((t) => t.active = eventsMask & t.bit);

                    // Filters gant events
                    let applyBits = applyTags & g.bits;
                    if (applyBits) {
                        events = events.filter((e) => applyBits & e.tags);
                    }
                });

                if (!events.length) {
                    return events;
                }

                events = masonry(events);

                let firstMonth = monthBeginning(events[0].start);
                let lastMonth = monthBeginning(events.reduce((r, e) => r < e.end ? e.end : r, firstMonth));

                this.months = getMonths(today, firstMonth, lastMonth, weekendList);
                this.width = this.months.reduce((r, m) => r + m.days.length, 0) * dayWidth;
                this.height = events.reduce((r, e) => Math.max(r, e.voffset), 0) + eventHeight * 2;

                const canvas = document.createElement('canvas');
                canvas.height = 1;
                canvas.width = this.width;
                const ctx = canvas.getContext("2d");

                let z = 0;
                for (let x = 0; x < this.months.length; x++){
                    const m = this.months[x];
                    for (let y = 0; y < m.days.length; y++){
                        ctx.fillStyle = m.days[y].is_weekend ? '#fafafa' : '#fff';
                        ctx.fillRect(z * dayWidth, 0, dayWidth, 1);
                        z++
                    }
                }

                this.bgUrl = canvas.toDataURL("image/png");
                return events;
            }
        }
    });
}


function monthBeginning(date) {
    let beginning = date.clone();
    beginning.startOf('month');
    return beginning;
}

function getEvents(firstMonth, eventSource, tagGroups) {
    let eventList = [];

    for (let i = 0; i < eventSource.length; i++){
        let source = eventSource[i];
        start = moment(source.start, dateFormat);
        end = moment(source.end, dateFormat);

        // Skips old events
        if (end < firstMonth) {
            continue;
        }

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
           search: source.title.toLowerCase(),
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

function getMonths(today, firstMonth, lastMonth, weekendList){
    let monthList = [];

    // Creates months rule
    const monthLen = lastMonth.diff(firstMonth, 'months');
    for (let i = 0; ; i++) {
        let month = moment(firstMonth),
            days = [];
        month.add(i, 'month');

        let total = month.daysInMonth();
        for (let y = 0; y < total; y++){
            let d = moment(month);
            d.date(y + 1)
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

        // Fixme: validate corner cases
        // May come infinite loop
        if (month >= lastMonth) {
            break;
        }
    }

    return monthList;
}

function masonry(eventList){
    let events = [],
        seen = [],
        startDate = monthBeginning(eventList[0].start)
    ;

    for (let i = 0; i < eventList.length; i++) {
        let event = Object.assign({}, eventList[i]);
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

renderTripper(weekendList, eventSource, tagGroups);
document.body.classList.add('active');
setTimeout(function(){
    let blocker = document.getElementById('blocker');
    blocker.parentNode.removeChild(blocker);
}, 400);
